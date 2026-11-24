"""Persistent event reminders; run the Flask command once per minute via cron."""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import socket

import click
from flask import flash, redirect, request, session, url_for
from flask_mail import Message
from models import db
from sqlalchemy.exc import IntegrityError

EASTERN = ZoneInfo('America/New_York')


def reminder_templates(event):
    details = f'{event[1]}\nDate: {event[2]}\nTime: {event[3]} - {event[4]}\nLocation: {event[5]}'
    return {
        'event_reminder': {'subject': f'Reminder: {event[1]} Event',
            'message': f'Hello,\n\nThis is a friendly reminder about the upcoming event:\n\n{details}\n\nPlease make sure to fulfill your commitment.\n\nThank you!'},
        'upcoming_event': {'subject': f'Upcoming Event: {event[1]}',
            'message': f"Hello,\n\nWe're excited to remind you about our upcoming event!\n\n{details}\n\nWe look forward to seeing you there!\n\nThank you!"},
        'last_minute': {'subject': f'Last-Minute Reminder: {event[1]}',
            'message': f'Hello,\n\nThis is a last-minute reminder about:\n\n{details}\n\nPlease confirm your participation.\n\nThank you!'},
    }


class ReminderSchedule(db.Model):
    __tablename__ = 'event_reminder_schedules'
    event_id = db.Column(db.Integer, primary_key=True)
    days_before = db.Column(db.Integer, nullable=False)
    send_time = db.Column(db.String(5), nullable=False)
    subject = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='scheduled')
    sent_count = db.Column(db.Integer, nullable=False, default=0)
    recipient_count = db.Column(db.Integer, nullable=False, default=0)
    revision = db.Column(db.Integer, nullable=False, default=1)


def scheduled_time(event_date, days_before, clock_time):
    if not 0 <= days_before <= 365:
        raise ValueError('Days before must be between 0 and 365.')
    clock = time.fromisoformat(clock_time)
    if clock.tzinfo or clock.second or clock.microsecond:
        raise ValueError('Choose a time in hours and minutes.')
    local = datetime.combine(event_date - timedelta(days=days_before), clock, EASTERN)
    # Reject a time skipped when clocks move forward; fall-back uses the first occurrence.
    if local.astimezone(timezone.utc).astimezone(EASTERN) != local:
        raise ValueError('That time does not exist when daylight saving time starts. Choose another time.')
    return local


def read_event(get_connection, event_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT date, archived FROM events WHERE id = %s', (event_id,))
            return cur.fetchone()
    finally:
        conn.close()


def recipient_emails(get_connection, event_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''SELECT DISTINCT es.responsible_email
                FROM event_signups es JOIN event_tables et ON es.table_id = et.id
                WHERE et.event_id = %s AND es.responsible_email IS NOT NULL
                  AND TRIM(es.responsible_email) <> '' ''', (event_id,))
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def send_due_reminders(app, mail, get_connection, now=None):
    now = now or datetime.now(timezone.utc)
    schedules = ReminderSchedule.query.filter_by(status='scheduled').all()
    for schedule in schedules:
        event = read_event(get_connection, schedule.event_id)
        if not event or event[1] or event[0] < now.astimezone(EASTERN).date():
            ReminderSchedule.query.filter_by(event_id=schedule.event_id,
                status='scheduled', revision=schedule.revision).update({'status': 'cancelled'})
            db.session.commit()
            continue
        try:
            due = scheduled_time(event[0], schedule.days_before, schedule.send_time)
        except ValueError:
            schedule.status = 'failed'
            db.session.commit()
            continue
        if due > now:
            continue
        # Claim before sending: overlapping cron runs cannot send the same schedule.
        claimed = ReminderSchedule.query.filter_by(event_id=schedule.event_id,
            status='scheduled', revision=schedule.revision).update({'status': 'sending'})
        db.session.commit()
        if not claimed:
            continue
        try:
            recipients = recipient_emails(get_connection, schedule.event_id)
            schedule.recipient_count = len(recipients)
            db.session.commit()
            failed = False
            for recipient in recipients:
                try:
                    message = Message(schedule.subject, recipients=[recipient],
                                      sender=app.config['MAIL_USERNAME'])
                    message.body = schedule.message
                    mail.send(message)
                except Exception:
                    failed = True
                    app.logger.exception('Scheduled reminder delivery failed for event %s', schedule.event_id)
                else:
                    schedule.sent_count += 1
                    db.session.commit()
            schedule.status = 'failed' if failed else ('sent' if recipients else 'no_recipients')
            db.session.commit()
        except Exception:
            db.session.rollback()
            schedule.status = 'failed'
            db.session.commit()
            app.logger.exception('Scheduled reminder failed for event %s', schedule.event_id)


def init_reminders(app, mail, get_connection):
    @app.route('/schedule_reminder/<int:event_id>', methods=['POST'])
    @app.route('/drsu/schedule_reminder/<int:event_id>/', methods=['POST'])
    def schedule_reminder(event_id):
        if 'email' not in session or not session.get('is_admin', False):
            flash('You must be an admin to schedule reminders.', 'danger')
            return redirect(url_for('homePage'))
        event = read_event(get_connection, event_id)
        if not event or event[1]:
            flash('Choose an active event to schedule a reminder.', 'danger')
            return redirect(url_for('homePage'))
        schedule = ReminderSchedule.query.filter_by(event_id=event_id).with_for_update().first()
        if schedule and schedule.status == 'sending':
            db.session.rollback()
            flash('This reminder is already sending. Its schedule cannot be changed now.', 'warning')
            return redirect(url_for('send_reminder', event_id=event_id))
        if request.form.get('action') == 'cancel':
            if schedule:
                schedule.status = 'cancelled'
                schedule.revision += 1
                db.session.commit()
            flash('Scheduled reminder cancelled.', 'success')
            return redirect(url_for('send_reminder', event_id=event_id))
        try:
            days = int(request.form.get('days_before', ''))
            clock = request.form.get('send_time', '')
            due = scheduled_time(event[0], days, clock)
            if due <= datetime.now(timezone.utc):
                raise ValueError('Choose a reminder time in the future.')
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            if not subject or not message:
                raise ValueError('Enter an email subject and message.')
        except (ValueError, OverflowError) as error:
            db.session.rollback()
            flash(str(error) or 'Enter valid reminder settings.', 'danger')
            return redirect(url_for('send_reminder', event_id=event_id))
        if not schedule:
            schedule = ReminderSchedule(event_id=event_id, revision=0)
            db.session.add(schedule)
        schedule.days_before = days
        schedule.send_time = due.strftime('%H:%M')
        schedule.subject = subject
        schedule.message = message
        schedule.status = 'scheduled'
        schedule.sent_count = 0
        schedule.recipient_count = 0
        schedule.revision += 1
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('This schedule was just changed. Reload the page and try again.', 'warning')
            return redirect(url_for('send_reminder', event_id=event_id))
        flash(f'Reminder scheduled for {due.strftime("%b %d, %Y at %I:%M %p %Z")}.', 'success')
        return redirect(url_for('send_reminder', event_id=event_id))

    @app.cli.command('send-due-reminders')
    def send_due_reminders_command():
        """Send due event reminders. Configure cron to run this every minute."""
        previous_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(30)
        try:
            send_due_reminders(app, mail, get_connection)
        finally:
            socket.setdefaulttimeout(previous_timeout)
        click.echo('Scheduled reminder check complete.')
