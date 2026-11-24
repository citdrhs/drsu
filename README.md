# CITSignups
 Purpose: To securely facilitate signing up for CIT events
#How to use
 - [General user manual](https://docs.google.com/document/d/1NkhQBlwExm0ig8_0kzieTy0qd2A5U5ilzeU700gAGMs/edit?tab=t.0#heading=h.ibdwoqy4tz5v)
 - [Admin user manual](https://docs.google.com/document/d/1EDiKRnn3x5_KuNLqAaoTwsqLbQ8ZOH2zH-c5zkG8RF4/edit?tab=t.0#heading=h.4qh0efgg0thm)
 - [Maintenance user manual](https://docs.google.com/document/d/1tfYS74Nv0NLoWpE0FAGV9mauBR90ubmLTtGlvcxQeu4/edit?tab=t.0#heading=h.vjhh2i1qbb99)
#
 Environment setup:
 - Set `DATABASE_URI` with your PostgreSQL host and port (example: `postgresql://user:pass@host:5433/dbname`)
 - Set `DB_PORT=5433` so direct `psycopg2` connections use the correct database port
 - Set `APP_PORT=5433` if you want Flask to run on port 5433 locally

 Progress:
 - Colors, font, and general theme of website established
 - Register and sign in functionality
 - Functionality for admin with admin code
 - Functionality to sign up to bring an item for an event and delete that item
 - Admin can create an event and then create tables for that event
#
 Future updates:
 - Calendar (in progress)
 - RSVP functionality

## Automatic event reminders

Admins can open **Send Reminder**, edit the email, choose **Days before the event**
and **Send at (Eastern time)**, then select **Save automatic reminder**. There is
one automatic reminder per event; saving again replaces it. The page shows its
status and offers cancellation. Manual **Send Reminders** still sends immediately.
Both methods use the edited subject and message.

Schedules are stored in the database and follow changes to the event date. At send
time, the worker gets the current participant list and sends once per email address.
Archived, deleted, or past events are skipped. Eastern daylight-saving time is
handled automatically; during the repeated fall hour the first occurrence is used.

### Server setup

These fork changes do not enable a live server job. After deploying:

1. Install `requirements.txt` in the application's virtual environment. Starting
   the app creates `event_reminder_schedules` through its existing `db.create_all()`.
2. Configure the existing mail and database environment variables. The cron process
   must use the same `.env` file/environment and app directory as the web service.
3. As the service account, add this cron entry (adjust the virtual environment path
   if necessary; the deployment workflow uses `/home/drsu/www`):

   ```cron
   * * * * * cd /home/drsu/www && /home/drsu/www/venv/bin/flask --app wsgi send-due-reminders
   ```

   For the nested application copy, run from its directory instead. Install only
   one job for the deployed application. Jobs check every minute and claim each
   schedule before sending, preventing overlapping runs from sending it twice.

Failed sends are shown on the reminder page, with the number sent. They are not
automatically retried, avoiding duplicate emails after a partial failure. If the
worker stops mid-send, the status stays **Sending**; check mail/server logs before
manually recovering that schedule. A successful SMTP submission is not proof of
inbox delivery. Monitor cron/server logs so an inactive worker is detected.

Run the isolated reminder tests with `python -m unittest discover -s tests`.

## Unlimited donations and holiday background

Set **Max Entries** to `999` for unlimited signups. The table shows the number signed
up and keeps its signup button available even after 999 entries. Other limits keep
their existing remaining-slots display.

The holiday image is `static/images/WinterGatheringHoliday.png` in both app copies.
To assign it to the existing Winter Gathering record after deploying, run
`scripts/set_winter_background.sql` once against the event database, or select the
image in **Edit Event**. This is a one-time choice; later image uploads remain editable.
The image was created with the built-in image generator using this prompt:

> Create a winter holiday background for a school event card: snowy evergreen branches, warm fairy lights, deep blue dusk, and open space for the event title. Wide landscape composition, welcoming and festive, polished illustration. No text, logos, or watermark.
