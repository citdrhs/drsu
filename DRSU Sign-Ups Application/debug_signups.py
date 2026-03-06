import os, psycopg2
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host='drhscit.org',
    database=os.environ.get('DB'),
    user=os.environ.get('DB_UN'),
    password=os.environ.get('DB_PW')
)
cur = conn.cursor()

event_id = 21

# Get event_signups table schema
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'event_signups' ORDER BY ordinal_position;")
columns = cur.fetchall()
print('event_signups columns:')
for col in columns:
    print(f'  {col[0]}')

# Get event_tables table schema
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'event_tables' ORDER BY ordinal_position;")
table_columns = cur.fetchall()
print('\nevent_tables columns:')
for col in table_columns:
    print(f'  {col[0]}')

# Check event_tables for this event
cur.execute('SELECT * FROM event_tables WHERE event_id = %s ORDER BY vieworder;', (event_id,))
tables = cur.fetchall()
print(f'\nEvent Tables for event {event_id}:')
for table in tables:
    print(f'  {table}')

# Check signups for this event
cur.execute('SELECT * FROM event_signups WHERE table_id IN (SELECT id FROM event_tables WHERE event_id = %s);', (event_id,))
signups = cur.fetchall()
print(f'\nSignups for event {event_id}:')
if signups:
    for signup in signups:
        print(f'  {signup}')
else:
    print('  No signups found')
    
# Check ALL recent signups
cur.execute('SELECT * FROM event_signups ORDER BY id DESC LIMIT 5;')
recent = cur.fetchall()
print(f'\nAll recent signups:')
for r in recent:
    print(f'  {r}')

cur.close()
conn.close()
