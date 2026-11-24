"""Verify real routes/templates against isolated SQLite fixtures and execute calendar JS.
Run: python tests/verify_event_flows.py . (requires Node.js for the calendar click).
No production database, files, accounts, or emails are touched.
"""
import base64, contextlib, io, json, os, re, sqlite3, subprocess, sys, tempfile, types
from datetime import date
from pathlib import Path
from unittest.mock import patch

root = Path(sys.argv[1]).resolve()
os.environ.update(DATABASE_URI='sqlite:///:memory:', SECRET_KEY='local-fixture-only', PYTHONIOENCODING='utf-8')
sys.path.insert(0, str(root))
sqlite3.register_converter('BOOLEAN', lambda value: bool(int(value)))
checks = []
def check(name, condition):
    checks.append((name, bool(condition)))

with tempfile.TemporaryDirectory(prefix='drsu-events-') as tmp:
    temp = Path(tmp)
    image_dir = temp / 'static' / 'images'
    image_dir.mkdir(parents=True)
    database = temp / 'fixture.sqlite'
    opened = []
    def connect_raw():
        connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        opened.append(connection)
        return connection
    with connect_raw() as conn:
        conn.executescript('''
        CREATE TABLE user (email TEXT PRIMARY KEY, first_name TEXT, last_name TEXT);
        CREATE TABLE events (id INTEGER PRIMARY KEY, name TEXT, date DATE, start_time TEXT,
          end_time TEXT, location TEXT, contact TEXT, file_name TEXT, event_note TEXT,
          legacy_background TEXT DEFAULT 'old.png', archived BOOLEAN DEFAULT 0);
        CREATE TABLE event_tables (id INTEGER PRIMARY KEY, event_id INTEGER, category TEXT,
          maxentries INTEGER, vieworder INTEGER, notes TEXT);
        CREATE TABLE event_signups (id INTEGER PRIMARY KEY, table_id INTEGER, responsible_name TEXT, item_name TEXT, responsible_email TEXT, comment TEXT);
        INSERT INTO user VALUES ('contact@example.test', 'Shlok', 'Joshi');
        INSERT INTO events VALUES (1, 'Winter Gathering', '2026-12-16', '11:35', '12:35',
          'SC4', 'contact@example.test', 'current.png', 'Bring donations', 'old.png', 0);
        INSERT INTO events VALUES (2, 'Archived Gathering', '2026-12-15', '11:35', '12:35',
          'SC4', 'contact@example.test', 'archived.png', '', 'old-archive.png', 1);
        ''')
    class Cursor:
        def __init__(self, cursor): self.cursor = cursor
        def execute(self, query, params=()):
            if query.lstrip().startswith('ALTER TABLE'): return self
            self.cursor.execute(query.replace('public.user', 'user').replace('%s', '?'), params)
            return self
        def fetchall(self): return self.cursor.fetchall()
        def fetchone(self): return self.cursor.fetchone()
        def __enter__(self): return self
        def __exit__(self, *args): self.close()
        def close(self): self.cursor.close()
    class Connection:
        def __init__(self): self.conn = connect_raw()
        def cursor(self): return Cursor(self.conn.cursor())
        def commit(self): self.conn.commit()
        def close(self): self.conn.close()
    source = (root / 'app.py').read_text(encoding='utf-8')
    module = types.ModuleType('app')
    module.__file__ = str(root / 'app.py')
    sys.modules['app'] = module
    with patch('dotenv.load_dotenv', return_value=False), patch('psycopg2.connect', side_effect=lambda **kwargs: Connection()), patch('flask_mail.Mail.send', side_effect=AssertionError('No email permitted')), contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        app = module.create_app()
        app.config.update(TESTING=True)
        # Keep uploaded files isolated from the repository and the real service.
        module.__file__ = str(temp / 'app.py')
        app.static_folder = str(temp / 'static')
        client = app.test_client()
        def login(admin):
            with client.session_transaction() as session:
                session['email'] = 'contact@example.test'
                session['is_admin'] = admin
        for admin in (False, True):
            login(admin)
            home = client.get('/drsu/homePage/').get_data(as_text=True)
            check('contact name, admin=' + str(admin), '<b>Contact:</b> Shlok Joshi' in home)
            check('current background, admin=' + str(admin), '/static/images/current.png' in home and '/static/images/old.png' not in home)
            check('archived events hidden, admin=' + str(admin), 'Archived Gathering' not in home)
        login(True)
        archived = client.get('/drsu/archived_events/').get_data(as_text=True)
        check('archived contact name', '<b>Contact:</b> Shlok Joshi' in archived)
        check('archived background', '/static/images/archived.png' in archived)
        # Execute the rendered calendar JS and invoke the actual click handler.
        js_runner = r'''
const fs = require('fs'), vm = require('vm');
const script = JSON.parse(fs.readFileSync(0, 'utf8'));
const nodes = [];
function element() { const el = { children: [], handlers: {}, style: {}, classList: { add() {} }, appendChild(x) { this.children.push(x); }, addEventListener(n, fn) { this.handlers[n] = fn; } }; nodes.push(el); return el; }
const elements = {};
const window = { location: { href: '' } };
class FixedDate extends Date { constructor(...args) { super(...(args.length ? args : ['2026-12-01T12:00:00'])); } }
vm.runInNewContext(script, { document: { getElementById(id) { return elements[id] ||= element(); }, createElement: element }, window, Date: FixedDate });
const event = nodes.find(n => typeof n.textContent === 'string' && n.textContent.startsWith('Winter Gathering @'));
event.handlers.click({ stopPropagation() {} });
process.stdout.write(window.location.href);
'''
        for mount in ('', '/drsu'):
            html = client.get('/drsu/calendar/', environ_overrides={'SCRIPT_NAME': mount}).get_data(as_text=True)
            script = re.search(r'<script>\s*(.*?)</script>', html, re.S).group(1)
            target = subprocess.check_output(['node', '-e', js_runner], input=json.dumps(script).encode()).decode()
            expected = mount + '/drsu/viewEvent/1/'
            check('calendar click with mount ' + repr(mount), target == expected)
            check('calendar excludes archived events ' + repr(mount), 'Archived Gathering' not in script)
            if target.startswith(mount):
                response = client.get(target[len(mount):], environ_overrides={'SCRIPT_NAME': mount})
                check('event opens with mount ' + repr(mount), response.status_code == 200 and 'Winter Gathering Signup' in response.get_data(as_text=True))
        form = dict(event_id='1', event_name='Winter Gathering', event_date='2026-12-16', start_time='11:35', end_time='12:35', location='SC4', contact_email='contact@example.test', note='Bring donations')
        png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
        response = client.post('/drsu/add_event/', data={**form, 'background_image': (io.BytesIO(png), 'new background.png')}, content_type='multipart/form-data', follow_redirects=True)
        check('edited upload displayed', response.status_code == 200 and '/static/images/new_background.png' in response.get_data(as_text=True))
        check('uploaded image served', client.get('/static/images/new_background.png').data == png)
        response = client.post('/drsu/add_event/', data={**form, 'note': 'Updated note'}, follow_redirects=True)
        check('edit without upload preserves background', '/static/images/new_background.png' in response.get_data(as_text=True))
        response = client.post('/drsu/add_event/', data={**form, 'event_id': '', 'event_name': 'New Event', 'background_image': (io.BytesIO(png), 'created.png')}, content_type='multipart/form-data', follow_redirects=True)
        check('new event upload displayed', response.status_code == 200 and '/static/images/created.png' in response.get_data(as_text=True))
        with connect_raw() as conn:
            conn.execute("UPDATE events SET contact='missing@example.test' WHERE id=1")
        home = client.get('/drsu/homePage/').get_data(as_text=True)
        check('missing contact has no boolean name', '<b>Contact:</b>   -' in home and 'False' not in re.search(r'<p><b>Contact:</b>(.*?)</p>', home).group(1))
        # Verify unlimited tables, manual reminders, and the real schedule form together.
        with connect_raw() as conn:
            conn.execute("INSERT INTO event_tables VALUES (1, 1, 'Food Donations', 999, 1, '')")
            conn.commit()
        empty = client.get('/drsu/viewEvent/1/').get_data(as_text=True)
        check('unlimited label', 'Unlimited signups (0 signed up)' in empty and '999/999' not in empty)
        with connect_raw() as conn:
            conn.executemany("INSERT INTO event_signups (table_id, responsible_name, item_name, responsible_email, comment) VALUES (1, 'Test User', 'Cans', 'contact@example.test', '')", [() for _ in range(1000)])
            conn.commit()
        full = client.get('/drsu/viewEvent/1/').get_data(as_text=True)
        check('unlimited beyond 999', 'Unlimited signups (1000 signed up)' in full and 'class="big-button signUpButton"' in full)
        with patch('flask_mail.Mail.send') as send:
            response = client.post('/drsu/send_reminder/1/', data=dict(template='event_reminder', subject='Edited subject', message='My custom message'))
            check('manual reminder succeeds', response.status_code == 302 and send.call_count == 1)
            check('manual reminder preserves edits', send.call_args.args[0].subject == 'Edited subject' and send.call_args.args[0].body == 'My custom message')
        from datetime import timedelta
        with connect_raw() as conn:
            conn.execute("UPDATE events SET date=? WHERE id=1", (date.today() + timedelta(days=10),))
            conn.commit()
        response = client.post('/drsu/schedule_reminder/1/', data=dict(days_before='2', send_time='09:30', subject='Scheduled subject', message='Scheduled message'), follow_redirects=True)
        html = response.get_data(as_text=True)
        check('actual schedule form and status', response.status_code == 200 and 'Scheduled subject' in html and 'Scheduled message' in html and 'Cancel automatic reminder' in html)
        with app.app_context():
            for first, last, is_admin, email in [
                ('Test', 'Delta', True, 'delta@example.test'),
                ('Test', 'Beta', False, 'beta@example.test'),
                ('Test', 'Charlie', True, 'charlie@example.test'),
                ('Test', 'Alpha', False, 'alpha@example.test'),
            ]:
                module.db.session.add(module.User(first_name=first, last_name=last, is_admin=is_admin, email=email, password='unused', grade='10'))
            module.db.session.commit()
            for direction, expected in [('desc', ['Test Charlie', 'Test Delta', 'Test Alpha', 'Test Beta']), ('asc', ['Test Alpha', 'Test Beta', 'Test Charlie', 'Test Delta'])]:
                html = client.get('/drsu/manage_admins/?sort_by=permission&sort_order=' + direction).get_data(as_text=True)
                check('permission order ' + direction, re.findall(r'<td>(Test [A-Za-z]+)</td>', html) == expected)
            html = client.get('/drsu/manage_admins/?sort_by=permission&sort_order=desc&search=alpha').get_data(as_text=True)
            check('permission search filters correctly', re.findall(r'<td>(Test [A-Za-z]+)</td>', html) == ['Test Alpha'])
            check('search retains permission ordering', 'name="sort_by" value="permission"' in html and 'name="sort_order" value="desc"' in html)
            html = client.get('/drsu/manage_admins/').get_data(as_text=True)
            check('default name order retained', re.findall(r'<td>(Test [A-Za-z]+)</td>', html) == ['Test Alpha', 'Test Beta', 'Test Charlie', 'Test Delta'])
        login(False)
        check('permission sort stays admin-only', client.get('/drsu/manage_admins/?sort_by=permission').status_code == 302)
    for connection in opened: connection.close()
    failures = [name for name, passed in checks if not passed]
    print(f'{root.name}: {len(checks) - len(failures)}/{len(checks)} passed')
    for failure in failures: print('  FAIL: ' + failure)
    if failures: sys.exit(1)
