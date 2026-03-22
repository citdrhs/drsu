import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except:
    pass

conn = psycopg2.connect(
    port=os.environ.get('DB_PORT', 5433),
    host=os.environ.get('DB_HOST', 'CITMAIN'),
    database=os.environ.get('DB'),
    user=os.environ.get('DB_UN'),
    password=os.environ.get('DB_PW')
)
cur = conn.cursor()
cur.execute("ALTER TABLE event_tables ADD COLUMN IF NOT EXISTS notes TEXT;")
conn.commit()
print("✓ Added notes column to event_tables")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'event_tables';")
print("Columns:", [r[0] for r in cur.fetchall()])
cur.close()
conn.close()
