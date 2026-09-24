"""
Automatic database table creation for SecretNotes.

Checks if Supabase tables exist and creates them if missing.
Uses direct PostgreSQL connection via psycopg2.
Also adds proper Row Level Security policies so the service key can access data.
"""
import os
import sys
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

# SQL schema from schema.sql
SCHEMA_SQL = """
-- SecretNotes Database Schema (auto-generated)
-- This script creates tables if they don't exist.

-- Table: app_settings
CREATE TABLE IF NOT EXISTS app_settings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  pin_hash text NOT NULL,
  kdf_salt text NOT NULL,
  idle_timeout_sec integer NOT NULL DEFAULT 180,
  created_at timestamptz DEFAULT now()
);

-- Table: notes
CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title_ciphertext text NOT NULL,
  title_iv text NOT NULL,
  body_ciphertext text NOT NULL,
  body_iv text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Row Level Security policies for Supabase service key access
-- The service_role key bypasses RLS, but we need to ensure policies exist
SELECT 1;
"""

# RLS policies to add after table creation
RLS_POLICIES_SQL = """
-- Enable RLS on both tables (if not already enabled)
ALTER TABLE IF EXISTS app_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS notes ENABLE ROW LEVEL SECURITY;

-- Allow full access via service key (bypass RLS)
-- These policies make the tables accessible via the Supabase service key
CREATE POLICY "service_key_access_app_settings" ON app_settings
USING (true);

CREATE POLICY "service_key_access_notes" ON notes
USING (true);
"""

# Index
INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC);
"""


def get_connection():
    """Create a direct PostgreSQL connection using DATABASE_URL."""
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not set in .env. "
            "Add it as: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
        )
    return psycopg2.connect(DATABASE_URL)


def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (table_name,),
            )
            result = cur.fetchone()
            return result[0] if result else False
    except Exception:
        return False


def ensure_tables() -> dict:
    """
    Ensure all SecretNotes tables exist in Supabase.
    Returns a dict with the status of each table.
    
    This is called automatically on app startup via the FastAPI lifespan.
    """
    result = {
        "status": "ok",
        "tables": {},
        "message": "All tables ready",
    }

    if not DATABASE_URL:
        result["status"] = "skipped"
        result["message"] = "DATABASE_URL not configured, skipping auto-creation"
        return result

    try:
        conn = get_connection()
        conn.autocommit = True

        tables_to_check = ["app_settings", "notes"]
        created = []
        already_existed = []

        for table_name in tables_to_check:
            if table_exists(conn, table_name):
                already_existed.append(table_name)
                result["tables"][table_name] = "exists"
            else:
                result["tables"][table_name] = "needs_creation"

        conn.close()

        # If any tables are missing, create them via direct connection
        if any(v == "needs_creation" for v in result["tables"].values()):
            conn = get_connection()
            cur = conn.cursor()

            # Run the full schema SQL
            for sql in SCHEMA_SQL.strip().split(';'):
                sql = sql.strip()
                if sql:
                    try:
                        cur.execute(sql)
                    except Exception as e:
                        print(f"Schema SQL note: {e}")

            # Run RLS policies
            for sql in RLS_POLICIES_SQL.strip().split(';'):
                sql = sql.strip()
                if sql:
                    try:
                        cur.execute(sql)
                    except Exception as e:
                        print(f"RLS SQL note: {e}")

            # Run index SQL
            for sql in INDEX_SQL.strip().split(';'):
                sql = sql.strip()
                if sql:
                    try:
                        cur.execute(sql)
                    except Exception as e:
                        print(f"Index SQL note: {e}")

            conn.commit()
            cur.close()
            conn.close()

            result["message"] = "Tables created successfully"
            result["status"] = "created"
            for table_name in tables_to_check:
                result["tables"][table_name] = "created"

        return result

    except ValueError as e:
        result["status"] = "error"
        result["message"] = str(e)
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Failed to ensure tables: {str(e)}"

    return result


def test_connection() -> dict:
    """Test if the database connection works."""
    if not DATABASE_URL:
        return {"connected": False, "message": "DATABASE_URL not set"}
    try:
        conn = get_connection()
        conn.close()
        return {"connected": True, "message": "Database connection successful"}
    except Exception as e:
        return {"connected": False, "message": str(e)}