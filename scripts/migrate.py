# ssc_event_form/scripts/migrate.py
from pathlib import Path
import sys, sqlite3
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from db import get_conn

migs = sorted((BASE / "migrations").glob("*.sql"))
if not migs:
    raise SystemExit("No migration files found")

with get_conn() as conn:
    for p in migs:
        try:
            conn.executescript(p.read_text(encoding="utf-8"))
            print("Applied:", p.name)
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Skipped (already applied):", p.name, "-", e)
                continue
            raise
    conn.commit()
