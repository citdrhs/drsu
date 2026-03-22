import psycopg2

# Read .env file
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.strip().split('=', 1)
            env_vars[key] = value

conn = psycopg2.connect(
    port=env_vars.get('DB_PORT', 5433),
    host=env_vars.get('DB_HOST', 'drhscit.org'),
    database=env_vars.get('DB'),
    user=env_vars.get('DB_UN'),
    password=env_vars.get('DB_PW')
)
cur = conn.cursor()

# Get the schema
cur.execute('''
    SELECT column_name, ordinal_position
    FROM information_schema.columns
    WHERE table_name = 'events'
    ORDER BY ordinal_position
''')

columns = cur.fetchall()
print('Events table columns:')
for col in columns:
    print(f'  [{col[1]-1}] {col[0]}')

# Fetch one event
cur.execute('SELECT * FROM events LIMIT 1')
event = cur.fetchone()
if event:
    print(f'\nSample event (total {len(event)} columns):')
    for i, value in enumerate(event):
        print(f'  [{i}] {value}')

cur.close()
conn.close()
