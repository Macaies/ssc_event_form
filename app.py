from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, jsonify, Response, send_from_directory
)
from datetime import datetime
import os, io, csv, xlsxwriter, re
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER, SECRET_KEY, GMAPS_API_KEY
from db import get_conn, init_db          # ensure your db.py defines init_db()
from modules import calendar, messaging   # calendar + email helpers
from locations_events import locations, event_types
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure DB table exists (SQLite or Postgres, per your db.py)
init_db()

# ---------------- Helpers ----------------
def _save(file_field: str):
    """Save an uploaded file (if provided) into UPLOAD_FOLDER; return stored filename or None."""
    f = request.files.get(file_field)
    if not f or not f.filename:
        return None
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    name = secure_filename(f.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], name)
    f.save(path)
    return name

def _to_iso(d, t):
    if not d:
        return None
    tt = (t or "00:00")
    return f"{d}T{tt}:00"

def _overlaps(a_start, a_end, b_start, b_end):
    """Return True if two [start, end) ranges overlap (ISO strings)."""
    if not a_start or not a_end or not b_start or not b_end:
        return False
    return a_start < b_end and a_end > b_start

# ---------- Classification Rules ----------
def classify_event(form):
    attendance = int(form.get("attendance", 0) or 0)
    alcohol = form.get("alcohol", "No")
    high_risk = form.get("high_risk", "No")
    traffic = form.get("traffic_mgmt", "No")
    vehicle_access = form.get("vehicle_access", "No")
    amplified = form.get("amplified_sound", "No")
    noise_level = int(form.get("noise_level", 0) or 0)
    total_days = int(form.get("total_days", 0) or 0)

    classification = "Self-assessable"
    if attendance >= 200: classification = "Assessable"
    if alcohol == "Yes": classification = "Assessable"
    if high_risk == "Yes": classification = "Assessable"
    if traffic == "Yes": classification = "Assessable"
    if vehicle_access == "Yes": classification = "Assessable"
    if amplified == "Yes" and noise_level > 95: classification = "Assessable"
    if total_days > 2: classification = "Assessable"
    return classification

# ---------- Conflict check ----------
def has_conflict(form):
    """Detect conflicts with APPROVED events at same place & overlapping time."""
    start_date = form.get("start_date")
    end_date   = form.get("end_date") or start_date
    start_time = form.get("start_time") or "00:00"
    end_time   = form.get("end_time") or "23:59"

    new_start = _to_iso(start_date, start_time)
    new_end   = _to_iso(end_date,   end_time)

    # Prefer exact ArcGIS feature id match if provided, else normalized location text
    fid = (form.get("arcgis_feature_id") or "").strip()
    loc = (form.get("location") or "").strip().lower()

    sql = """
      SELECT start_date, end_date, start_time, end_time, location, arcgis_feature_id
      FROM events
      WHERE status='Approved'
        AND (
              (arcgis_feature_id IS NOT NULL AND arcgis_feature_id <> '' AND arcgis_feature_id = ?)
           OR (LOWER(COALESCE(location,'')) = ?)
        )
        AND (
              date(?) <= date(end_date) AND date(?) >= date(start_date)
        )
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, (fid, loc, start_date, end_date))
        rows = cur.fetchall()

    # refine via time overlap
    for r in rows:
        r_start = _to_iso(r["start_date"], r["start_time"])
        r_end   = _to_iso(r["end_date"],   r["end_time"])
        if _overlaps(new_start, new_end, r_start, r_end):
            return True
    return False

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template(
        "index.html",
        gmaps_api_key=GMAPS_API_KEY,
        locations=locations,
        event_types=event_types,
    )

@app.route("/api/locations")
def api_locations():
    return jsonify({"locations": locations, "event_types": event_types})

@app.route("/submit", methods=["POST"])
def submit():
    form = request.form.to_dict()

    # map frontend → DB fields
    form["applicant_name"]  = form.get("organizer_name", "")
    form["applicant_email"] = form.get("contact_email", "")
    form["applicant_phone"] = form.get("contact_phone", "")
    form["location"]        = form.get("venue", "")

    # file uploads
    insurance_file = _save("insurance_doc")
    site_map       = _save("site_map")
    other_files    = _save("other_docs")

    # classification + conflict
    classification = classify_event(form)
    conflict = has_conflict(form)
    status = "Approved" if (classification == "Self-assessable" and not conflict) else "Pending"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # insert
    cols = [
        "event_type", "applicant_name", "applicant_email", "applicant_phone",
        "event_name", "location", "start_date", "end_date", "start_time", "end_time",
        "attendance", "alcohol", "high_risk", "traffic_mgmt", "vehicle_access",
        "amplified_sound", "noise_level", "total_days", "notes",
        "insurance_file", "site_map", "other_files",
        "latitude", "longitude", "arcgis_feature_id", "arcgis_feature_name", "arcgis_layer",
        "classification", "status", "created_at"
    ]
    vals = (
        form.get("event_type"),
        form.get("applicant_name"),
        form.get("applicant_email"),
        form.get("applicant_phone"),
        form.get("event_name"),
        form.get("location"),
        form.get("start_date"),
        form.get("end_date") or form.get("start_date"),
        form.get("start_time"),
        form.get("end_time"),
        int(form.get("attendance", 0) or 0),
        form.get("alcohol", "No"),
        form.get("high_risk", "No"),
        form.get("traffic_mgmt", "No"),
        form.get("vehicle_access", "No"),
        form.get("amplified_sound", "No"),
        int(form.get("noise_level", 0) or 0),
        int(form.get("total_days", 1) or 1),
        form.get("notes"),
        insurance_file, site_map, other_files,
        request.form.get("latitude") or None,
        request.form.get("longitude") or None,
        request.form.get("arcgis_feature_id") or None,
        request.form.get("arcgis_feature_name") or None,
        request.form.get("arcgis_layer") or None,
        classification, status, now
    )
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO events ({','.join(cols)}) VALUES ({placeholders})"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, vals)
        conn.commit()
        new_id = cur.lastrowid

    # email receipt (best-effort)
    try:
        messaging.send_submission_receipt(
            to_addr=form.get("applicant_email") or "",
            event_name=form.get("event_name") or "",
            applicant_name=form.get("applicant_name") or "",
            start_date=form.get("start_date") or "",
            start_time=form.get("start_time") or "",
            end_date=form.get("end_date") or form.get("start_date") or "",
            end_time=form.get("end_time") or "",
            venue=form.get("location") or form.get("venue") or "",
            classification=classification,
            conflict=bool(conflict),
        )
    except Exception as e:
        print("Email send (receipt) failed:", e)

    # auto-reserve calendar if self-assessable & no conflict
    if classification == "Self-assessable" and not conflict:
        try:
            calendar.reserve(
                title=form.get("event_name"),
                date_str=form.get("start_date"),
                start_time=form.get("start_time"),
                finish_time=form.get("end_time"),
                auto=True
            )
        except Exception as e:
            print("Calendar reserve failed:", e)

    return redirect(url_for(
        "success",
        classification=classification,
        applicant_name=form.get("applicant_name", ""),
        event_name=form.get("event_name", ""),
        conflict=("1" if conflict else "0")
    ))

@app.route("/api/check_conflict", methods=["POST"])
def api_check_conflict():
    data = request.get_json(force=True)
    form = {
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date") or data.get("start_date"),
        "start_time": data.get("start_time") or "00:00",
        "end_time": data.get("end_time") or "23:59",
        "arcgis_feature_id": data.get("arcgis_feature_id") or "",
        "location": data.get("location") or data.get("venue") or "",
    }
    return jsonify({"conflict": has_conflict(form)})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)

@app.route("/success")
def success():
    return render_template("success.html",
        classification=request.args.get("classification","Self-assessable"),
        conflict=request.args.get("conflict","0")
    )

@app.route("/admin")
def admin():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()

    query = "SELECT * FROM events WHERE 1=1"
    params = []
    if q:
        query += " AND (applicant_name LIKE ? OR event_type LIKE ? OR event_name LIKE ?)"
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if status:
        if status in ("Self-assessable", "Assessable"):
            query += " AND classification = ?"
            params.append(status)
        elif status in ("Pending", "Approved", "Rejected", "Cancelled"):
            query += " AND status = ?"
            params.append(status)
    query += " ORDER BY created_at DESC"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        applications = cur.fetchall()

    return render_template("admin.html", applications=applications)

@app.route("/export/<format>")
def export_data(format):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM events ORDER BY created_at DESC")
        rows = cur.fetchall()

    if format == "csv":
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(list(rows[0].keys()) if rows else [])
        for r in rows:
            cw.writerow([r[k] for k in r.keys()])
        return Response(si.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition":"attachment;filename=events.csv"})

    if format == "xlsx":
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {"in_memory": True})
        ws = wb.add_worksheet("Events")
        if rows:
            for c, key in enumerate(rows[0].keys()):
                ws.write(0, c, key)
        for r_i, r in enumerate(rows, start=1):
            for c, key in enumerate(r.keys()):
                ws.write(r_i, c, r[key])
        wb.close()
        output.seek(0)
        return send_file(output, as_attachment=True,
                         download_name="events.xlsx",
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return "Unsupported format", 400

@app.route("/api/events")
def api_events():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, event_name, start_date, end_date, start_time, end_time,
                   classification, status, location
            FROM events
            ORDER BY start_date ASC, start_time ASC
        """)
        rows = cur.fetchall()

    def to_iso(d, t):
        if not d: return None
        return f"{d}T{(t or '00:00')}:00"

    status_class = {
        "Approved": "fc-approved",
        "Pending":  "fc-pending",
        "Rejected": "fc-rejected",
        "Cancelled":"fc-rejected",
    }

    # Title shows "Event – Location"
    events = [{
        "id": r["id"],
        "title": f"{r['event_name']} – {r['location'] or ''}".strip(),
        "start": to_iso(r["start_date"], r["start_time"]),
        "end":   to_iso(r["end_date"],   r["end_time"]),
        "extendedProps": {
            "classification": r["classification"],
            "status": r["status"],
            "location": r["location"]
        },
        "className": status_class.get(r["status"], "fc-pending")
    } for r in rows]

    return jsonify(events)

@app.route("/calendar")
def calendar_view():
    return render_template("calendar.html")

@app.route("/admin/event/<int:event_id>/<action>")
def update_event_status(event_id, action):
    new_status = None
    if action == "approve": new_status = "Approved"
    if action == "reject":  new_status = "Rejected"
    if not new_status:
        return "Invalid action", 400

    with get_conn() as conn:
        cur = conn.cursor()
        # fetch row first
        cur.execute("SELECT * FROM events WHERE id=?", (event_id,))
        row = cur.fetchone()
        if not row:
            return "Not found", 404

        # update
        cur.execute("UPDATE events SET status=? WHERE id=?", (new_status, event_id))
        conn.commit()

    # email after commit
    try:
        messaging.send_status_update(
            to_addr=row["applicant_email"] or "",
            event_name=row["event_name"] or "",
            new_status=new_status,
            start_date=row["start_date"] or "",
            start_time=row["start_time"] or "",
            end_date=row["end_date"] or row["start_date"] or "",
            end_time=row["end_time"] or "",
            venue=row["location"] or "",
            reason=None
        )
    except Exception as e:
        print("Email send (status update) failed:", e)

    return redirect(url_for("admin"))

@app.route("/api/event/<int:event_id>/status", methods=["POST"])
def api_update_status(event_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("Approved", "Pending", "Rejected", "Cancelled"):
        return jsonify({"ok": False, "error": "Invalid status"}), 400

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM events WHERE id=?", (event_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Not found"}), 404
        cur.execute("UPDATE events SET status=? WHERE id=?", (new_status, event_id))
        conn.commit()

    try:
        messaging.send_status_update(
            to_addr=row["applicant_email"] or "",
            event_name=row["event_name"] or "",
            new_status=new_status,
            start_date=row["start_date"] or "",
            start_time=row["start_time"] or "",
            end_date=row["end_date"] or row["start_date"] or "",
            end_time=row["end_time"] or "",
            venue=row["location"] or "",
            reason=None
        )
    except Exception as e:
        print("Email send (status update) failed:", e)

    return jsonify({"ok": True})

@app.route("/admin/quick_book", methods=["POST"])
def admin_quick_book():
    data = request.get_json(force=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cols = [
        "event_type", "applicant_name", "applicant_email", "applicant_phone",
        "event_name", "location", "start_date", "end_date", "start_time", "end_time",
        "attendance", "alcohol", "high_risk", "traffic_mgmt", "vehicle_access",
        "amplified_sound", "noise_level", "total_days", "notes",
        "insurance_file", "site_map", "other_files",
        "latitude", "longitude", "arcgis_feature_id", "arcgis_feature_name", "arcgis_layer",
        "classification", "status", "created_at"
    ]
    vals = (
        "AdminBooking", "", "", "",
        data.get("event_name","Untitled"),
        data.get("location",""),
        data.get("start_date"), data.get("end_date"),
        data.get("start_time"), data.get("end_time"),
        0, "No", "No", "No", "No",
        "No", 0, 1, "",
        None, None, None,
        None, None, None, None, None,
        "Self-assessable", "Approved", now
    )
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO events ({','.join(cols)}) VALUES ({placeholders})"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, vals)
        conn.commit()
    return jsonify({"ok": True})

# ---------- Minimal chatbot ----------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Very simple rule-based chatbot:
    - list event types & locations
    - quick conflict check: “Is <venue> free on 2025-09-20 10:00-12:00?”
    - common FAQs
    """
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "Hi! Ask me about event types, locations, or availability."})

    low = msg.lower()

    # event types
    if "event type" in low or "types" in low:
        return jsonify({"reply": "Available event types:\n• " + "\n• ".join(event_types[:20]) + ("\n… (and more)" if len(event_types) > 20 else "")})

    # locations
    if "location" in low or "park" in low or "venue" in low:
        sample = locations[:12]
        return jsonify({"reply": "Common venues (sample):\n• " + "\n• ".join(sample) + ("\n…Type to search more in the form’s Venue field." if len(locations) > len(sample) else "")})

    # quick availability parsing
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", msg)
    time_match = re.search(r"(\d{1,2}:\d{2})\s*[-to]\s*(\d{1,2}:\d{2})", low)
    venue_guess = None
    for loc in locations:
        if loc.lower() in low:
            venue_guess = loc
            break

    if date_match and time_match and venue_guess:
        start_date = date_match.group(1)
        start_time = time_match.group(1)
        end_time   = time_match.group(2)
        form = {
            "start_date": start_date,
            "end_date": start_date,
            "start_time": start_time,
            "end_time": end_time,
            "location": venue_guess,
            "arcgis_feature_id": ""
        }
        conflict = has_conflict(form)
        if conflict:
            return jsonify({"reply": f"Looks like **{venue_guess}** is **already booked** on **{start_date} {start_time}–{end_time}**. Try a different time or day."})
        else:
            return jsonify({"reply": f"**Good news!** I can’t see any approved bookings at **{venue_guess}** on **{start_date} {start_time}–{end_time}**. You can submit the form now."})

    # FAQs
    if "self-assess" in low or "self assess" in low:
        return jsonify({"reply": "Self-assessable generally means: under 200 attendees, no alcohol, no high-risk activities, no traffic management, no vehicle access, and amplified sound under 95 dB. If your answers fit, we auto-approve and reserve the slot."})
    if "how long" in low or "approval" in low or "review" in low:
        return jsonify({"reply": "Council staff review assessable applications within ~5 business days. You’ll receive an email update automatically when the status changes."})
    if "contact" in low or "help" in low:
        return jsonify({"reply": "You can submit via the online form. For complex cases, Council events team can assist—reply to the confirmation email once you submit."})

    # default
    return jsonify({"reply": "I can help with: event types, locations, and quick availability checks.\nTry: “Is Cotton Tree Park free on 2025-11-02 10:00-12:00?”"})

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    # If you still keep migrations, you can keep your guard here; otherwise remove:
    if not os.path.exists("migrations/001_init.sql"):
        # Comment out the next line if you don't use migrations anymore.
        # raise SystemExit("Missing migrations/001_init.sql. Create it first.")
        pass
    app.run(debug=True)
