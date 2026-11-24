"""Run with python -m unittest discover -s tests. Uses SQLite and loopback SMTP only."""
import tempfile
import unittest
import socketserver
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from email import policy
from email.parser import BytesParser
from pathlib import Path
from unittest.mock import Mock

from flask import Flask
from flask_mail import Mail
from models import db
from reminders import (EASTERN, ReminderSchedule, init_reminders,
                       scheduled_time, send_due_reminders)


class Cursor:
    def __init__(self, fixture):
        self.fixture = fixture

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute(self, query, params):
        self.query, self.event_id = query, params[0]

    def fetchone(self):
        if getattr(self.fixture, 'read_barrier', None):
            self.fixture.read_barrier.wait(timeout=5)
        return self.fixture.events.get(self.event_id)

    def fetchall(self):
        return [(email,) for email in set(self.fixture.recipients.get(self.event_id, []))]


class LocalSMTP(socketserver.StreamRequestHandler):
    """Capture SMTP on loopback without forwarding email anywhere."""
    def handle(self):
        self.request.settimeout(5)
        self.wfile.write(b'220 local test server\r\n')
        while line := self.rfile.readline():
            command = line.split(b' ', 1)[0].strip().upper()
            if command == b'DATA':
                self.wfile.write(b'354 End with a dot\r\n')
                lines = []
                while (line := self.rfile.readline()) not in (b'.\r\n', b''):
                    lines.append(line[1:] if line.startswith(b'..') else line)
                self.server.messages.append(BytesParser(policy=policy.default).parsebytes(b''.join(lines)))
                self.wfile.write(b'250 Captured\r\n')
            elif command == b'QUIT':
                self.wfile.write(b'221 Bye\r\n')
                break
            else:
                self.wfile.write(b'250 OK\r\n')


class ReminderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.uri = 'sqlite:///' + str(Path(self.temp.name) / 'reminders.sqlite')
        self.events = {1: (date.today() + timedelta(days=10), False)}
        self.recipients = {1: ['one@example.test', 'two@example.test']}
        self.mail = Mock()
        self.conn = Mock()
        self.conn.cursor.side_effect = lambda: Cursor(self)
        self.get_connection = lambda: self.conn
        self.app = self.make_app()
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session.update(email='admin@example.test', is_admin=True)

    def make_app(self):
        app = Flask(__name__)
        app.config.update(SECRET_KEY='test', SQLALCHEMY_DATABASE_URI=self.uri,
                          TESTING=True, MAIL_USERNAME='sender@example.test')
        db.init_app(app)
        app.add_url_rule('/home', 'homePage', lambda: 'home')
        app.add_url_rule('/reminder/<int:event_id>', 'send_reminder', lambda event_id: 'reminder')
        init_reminders(app, self.mail, self.get_connection)
        return app

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()
        self.temp.cleanup()

    def save(self, **changes):
        form = dict(days_before='2', send_time='09:30',
                    subject='Our edited subject', message='Our edited message')
        form.update(changes)
        return self.client.post('/drsu/schedule_reminder/1/', data=form)

    def due(self):
        return scheduled_time(self.events[1][0], 2, '09:30').astimezone(timezone.utc)

    def run_due(self, now=None):
        send_due_reminders(self.app, self.mail, self.get_connection, now or self.due())

    def test_save_without_participants_and_update_existing(self):
        self.recipients[1] = []
        self.save()
        self.save(days_before='3', send_time='10:00')
        self.assertEqual(ReminderSchedule.query.count(), 1)
        schedule = db.session.get(ReminderSchedule, 1)
        self.assertEqual((schedule.days_before, schedule.send_time), (3, '10:00'))
        self.assertEqual(schedule.message, 'Our edited message')
        self.mail.send.assert_not_called()

    def test_uses_current_participants_and_does_not_repeat(self):
        self.save()
        self.run_due(self.due() - timedelta(seconds=1))
        self.mail.send.assert_not_called()
        self.recipients[1] += ['late@example.test', 'one@example.test']
        self.run_due()
        self.run_due()
        self.assertEqual(self.mail.send.call_count, 3)
        self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'sent')
        for call in self.mail.send.call_args_list:
            self.assertEqual(call.args[0].subject, 'Our edited subject')
            self.assertEqual(call.args[0].body, 'Our edited message')

    def test_schedule_survives_app_restart(self):
        self.save()
        another_app = self.make_app()
        with another_app.app_context():
            self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'scheduled')
            send_due_reminders(another_app, self.mail, self.get_connection, self.due())
            self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'sent')
            db.session.remove()
            db.engine.dispose()
        self.assertEqual(self.mail.send.call_count, 2)

    def test_overlapping_workers_skip_claimed_schedule(self):
        self.save()
        another_app = self.make_app()
        def overlapping_worker(message):
            with another_app.app_context():
                send_due_reminders(another_app, self.mail, self.get_connection, self.due())
                db.session.remove()
                db.engine.dispose()
        self.mail.send.side_effect = overlapping_worker
        self.run_due()
        self.assertEqual(self.mail.send.call_count, 2)
        self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'sent')

    def test_workers_racing_for_the_same_pending_schedule_send_once(self):
        self.save()
        due = self.due()
        self.read_barrier = threading.Barrier(2)
        def worker():
            with self.app.app_context():
                send_due_reminders(self.app, self.mail, self.get_connection, due)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker) for _ in range(2)]
            for future in futures:
                future.result(timeout=10)
        self.read_barrier = None
        db.session.expire_all()
        self.assertEqual(self.mail.send.call_count, 2)
        self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'sent')

    def test_actual_smtp_delivery_to_local_capture_server(self):
        self.save()
        with socketserver.ThreadingTCPServer(('127.0.0.1', 0), LocalSMTP) as server:
            server.messages = []
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                self.app.config.update(MAIL_SERVER='127.0.0.1', MAIL_PORT=server.server_address[1],
                    MAIL_USE_TLS=False, MAIL_USE_SSL=False, MAIL_USERNAME=None, MAIL_PASSWORD=None,
                    MAIL_DEFAULT_SENDER='sender@example.test', MAIL_SUPPRESS_SEND=False)
                mail = Mail(self.app)
                send_due_reminders(self.app, mail, self.get_connection, self.due())
                self.assertEqual(len(server.messages), 2)
                self.assertEqual({str(message['To']) for message in server.messages}, set(self.recipients[1]))
                for message in server.messages:
                    self.assertEqual(message['Subject'], 'Our edited subject')
                    self.assertEqual(message.get_content().strip(), 'Our edited message')
                self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'sent')
            finally:
                server.shutdown()
                thread.join(timeout=5)

    def test_cancel_prevents_send(self):
        self.save()
        self.client.post('/drsu/schedule_reminder/1/', data={'action': 'cancel'})
        self.run_due()
        self.mail.send.assert_not_called()

    def test_invalid_settings_and_nonadmins_cannot_schedule(self):
        for changes in ({'days_before': '-1'}, {'days_before': '366'},
                        {'days_before': 'no'}, {'send_time': '25:00'},
                        {'subject': ' '}, {'message': ''}):
            self.save(**changes)
            self.assertEqual(ReminderSchedule.query.count(), 0)
        self.events[1] = (date.today() - timedelta(days=1), False)
        self.save()
        self.assertEqual(ReminderSchedule.query.count(), 0)
        with self.client.session_transaction() as session:
            session['is_admin'] = False
        self.save()
        self.assertEqual(ReminderSchedule.query.count(), 0)

    def test_event_date_change_moves_reminder(self):
        self.save()
        original_due = self.due()
        self.events[1] = (self.events[1][0] + timedelta(days=3), False)
        self.run_due(original_due)
        self.mail.send.assert_not_called()
        self.run_due()
        self.assertEqual(self.mail.send.call_count, 2)

    def test_archived_or_deleted_events_are_cancelled(self):
        for event in (None, (date.today() + timedelta(days=10), True)):
            self.events[1] = (date.today() + timedelta(days=10), False)
            self.save()
            due = self.due()
            if event is None:
                del self.events[1]
            else:
                self.events[1] = event
            self.run_due(due)
            self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'cancelled')
        self.mail.send.assert_not_called()

    def test_partial_failure_is_visible_and_not_retried(self):
        self.save()
        self.mail.send.side_effect = [None, RuntimeError('SMTP unavailable')]
        with self.assertLogs(self.app.logger, level='ERROR'):
            self.run_due()
        self.run_due()
        schedule = db.session.get(ReminderSchedule, 1)
        self.assertEqual((schedule.status, schedule.sent_count, schedule.recipient_count), ('failed', 1, 2))
        self.assertEqual(self.mail.send.call_count, 2)

    def test_no_recipients_does_not_claim_delivery(self):
        self.save()
        self.recipients[1] = []
        self.run_due()
        self.assertEqual(db.session.get(ReminderSchedule, 1).status, 'no_recipients')
        self.mail.send.assert_not_called()

    def test_sending_schedule_cannot_be_overwritten(self):
        self.save()
        schedule = db.session.get(ReminderSchedule, 1)
        schedule.status = 'sending'
        db.session.commit()
        self.save(message='Replacement')
        self.client.post('/drsu/schedule_reminder/1/', data={'action': 'cancel'})
        self.assertEqual(schedule.status, 'sending')
        self.assertEqual(schedule.message, 'Our edited message')

    def test_eastern_daylight_saving_offsets_and_invalid_time(self):
        self.assertEqual(scheduled_time(date(2027, 1, 15), 1, '09:00').utcoffset(), timedelta(hours=-5))
        self.assertEqual(scheduled_time(date(2027, 7, 15), 1, '09:00').utcoffset(), timedelta(hours=-4))
        with self.assertRaises(ValueError):
            scheduled_time(date(2027, 3, 14), 0, '02:30')

    def test_cli_runs_without_sending_future_reminders(self):
        self.save()
        result = self.app.test_cli_runner().invoke(args=['send-due-reminders'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.mail.send.assert_not_called()


if __name__ == '__main__':
    unittest.main()
