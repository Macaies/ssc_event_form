from db import get_conn as get_db


def reserve(title, date_str, start_time, finish_time, auto=True):
    """
    Records an event for the calendar feed.
    If auto=False we just flag 'Pending staff scheduling'.
    """
    if not title or not date_str:
        return "❌ Missing date/title"

    if not auto:
        return "🟡 Pending staff scheduling (assessable)"

    # Simple local calendar table (create if not exists)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS _calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, day TEXT, start_time TEXT, finish_time TEXT
        )
    """)
    cur.execute("INSERT INTO _calendar (title, day, start_time, finish_time) VALUES (?,?,?,?)",
                (title, date_str, start_time, finish_time))
    conn.commit()
    conn.close()
    return "✅ Auto-scheduled to calendar"

def get_events():
    """Return FullCalendar-compatible list."""
    conn = get_db()
    cur = conn.cursor()
    # from apps table
    cur.execute("SELECT event_name, event_date FROM applications")
    app_rows = cur.fetchall()
    # from local calendar table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS _calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, day TEXT, start_time TEXT, finish_time TEXT
        )
    """)
    cur.execute("SELECT title, day FROM _calendar")
    cal_rows = cur.fetchall()
    conn.close()

    events = []
    for r in app_rows:
        if r["event_name"] and r["event_date"]:
            events.append({"title": r["event_name"], "start": r["event_date"]})
    for r in cal_rows:
        events.append({"title": r["title"], "start": r["day"]})
    return events
