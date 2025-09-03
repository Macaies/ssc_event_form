# db.py
import os, sqlite3
from contextlib import contextmanager

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "events.db"))
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

_use_postgres = DATABASE_URL.startswith(("postgres://", "postgresql://"))

if _use_postgres:
    import psycopg2
    import psycopg2.extras

@contextmanager
def get_conn():
    if _use_postgres:
        conn = psycopg2.connect(DATABASE_URL)
        # row factory-ish
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                yield _PgConn(conn, cur)
        conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

class _PgConn:
    def __init__(self, conn, cur):
        self._conn = conn
        self._cur = cur
    def cursor(self):
        return self._cur
    def commit(self):
        self._conn.commit()
    def executescript(self, sql):
        # not used for PG; no-op or split by ';' if you need migrations
        for stmt in [s.strip() for s in sql.split(';') if s.strip()]:
            self._cur.execute(stmt)

def init_db():
    """Create table if not exists (works for both SQLite and PG)."""
    schema = """
    CREATE TABLE IF NOT EXISTS events (
      id SERIAL PRIMARY KEY,
      event_type TEXT,
      applicant_name TEXT NOT NULL,
      applicant_email TEXT NOT NULL,
      applicant_phone TEXT NOT NULL,
      event_name TEXT NOT NULL,
      location TEXT NOT NULL,
      start_date TEXT NOT NULL,
      end_date TEXT NOT NULL,
      start_time TEXT,
      end_time TEXT,
      attendance INTEGER DEFAULT 0,
      alcohol TEXT DEFAULT 'No',
      high_risk TEXT DEFAULT 'No',
      traffic_mgmt TEXT DEFAULT 'No',
      vehicle_access TEXT DEFAULT 'No',
      amplified_sound TEXT DEFAULT 'No',
      noise_level INTEGER DEFAULT 0,
      total_days INTEGER DEFAULT 1,
      notes TEXT,
      insurance_file TEXT,
      site_map TEXT,
      other_files TEXT,
      latitude TEXT,
      longitude TEXT,
      arcgis_feature_id TEXT,
      arcgis_feature_name TEXT,
      arcgis_layer TEXT,
      classification TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'Pending',
      created_at TEXT NOT NULL
    );
    """
    with get_conn() as conn:
        cur = conn.cursor()
        if isinstance(conn, sqlite3.Connection):
            conn.executescript(schema)
        else:
            conn.executescript(schema)
        conn.commit()
