import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Get DATABASE_URL from env or use the known one
DATABASE_URL = 'postgresql://postgres:xFYIJAJviJ4H0Mlh@db.uhgkqgqcmioobddalzbh.supabase.co:5432/postgres'

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Enable RLS
cur.execute('ALTER TABLE IF EXISTS app_settings ENABLE ROW LEVEL SECURITY;')
cur.execute('ALTER TABLE IF EXISTS notes ENABLE ROW LEVEL SECURITY;')

# Create RLS policies - use dollar-quoting to avoid quote issues
cur.execute("$$CREATE POLICY service_key_access_app_settings ON app_settings USING (true);$$")
cur.execute("$$CREATE POLICY service_key_access_notes ON notes USING (true);$$")

# Verify
cur.execute('SELECT id, pin_hash FROM app_settings LIMIT 1;')
print('app_settings:', cur.fetchone())

cur.execute('SELECT id FROM notes LIMIT 1;')
print('notes:', cur.fetchone())

print('RLS policies created successfully')
cur.close()
conn.close()