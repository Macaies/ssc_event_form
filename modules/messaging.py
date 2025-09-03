# modules/messaging.py
import smtplib, ssl
from email.message import EmailMessage
from typing import Optional

try:
    # same folder import pattern as your other modules
    from config import EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_FROM, EMAIL_USER, EMAIL_PASS
except Exception:
    # Fallbacks if config import path differs
    EMAIL_SMTP_HOST = "smtp.gmail.com"
    EMAIL_SMTP_PORT = 587
    EMAIL_FROM = "Sunshine Coast Council <no-reply@scc.example>"
    EMAIL_USER = ""
    EMAIL_PASS = ""

def _send_email(to_addr: str, subject: str, html: str, text: Optional[str] = None):
    """
    Low-level email sender using Gmail SMTP (TLS).
    Set EMAIL_USER, EMAIL_PASS in environment (see config.py).
    """
    if not EMAIL_USER or not EMAIL_PASS:
        print("[messaging] EMAIL_USER / EMAIL_PASS not set; skipping email send.")
        return False

    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_addr
    msg["Subject"] = subject
    if not text:
        text = "This message requires an HTML-capable email client."
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    return True

# ---------- High-level helpers ----------

def send_submission_receipt(to_addr: str, *, event_name: str, applicant_name: str,
                            start_date: str, start_time: str, end_date: str, end_time: str,
                            venue: str, classification: str, conflict: bool):
    subject = f"Your event application: {event_name}"
    status_line = (
        "Self-assessable (Reserved)" if (classification == "Self-assessable" and not conflict)
        else "Pending review"
    )
    conflict_msg = (
        "<p style='color:#8a6d3b;background:#fff3cd;padding:8px;border-radius:6px;'>"
        "Heads up: another booking exists at this venue/time. Your application is <strong>Pending</strong>."
        "</p>" if conflict else ""
    )
    html = f"""
    <div style="font-family:Arial,sans-serif">
      <h2>Thanks, {escape(applicant_name) or 'Applicant'} — we received your application</h2>
      <p><strong>Event:</strong> {escape(event_name)}<br>
         <strong>Venue:</strong> {escape(venue or '-') }<br>
         <strong>When:</strong> {escape(start_date)} {escape(start_time or '')} – {escape(end_date or start_date)} {escape(end_time or '')}<br>
         <strong>Status:</strong> {escape(status_line)}</p>
      {conflict_msg}
      <p>We’ll email you if we need more info. You can expect an update within 5 business days.</p>
      <hr>
      <p style="color:#888;font-size:12px">Sunshine Coast Council – Event Permit Prototype</p>
    </div>
    """
    text = f"""Thanks, {applicant_name or 'Applicant'} — we received your application.
Event: {event_name}
Venue: {venue or '-'}
When: {start_date} {start_time or ''} – {end_date or start_date} {end_time or ''}
Status: {status_line}
"""
    return _send_email(to_addr, subject, html, text)

def send_status_update(to_addr: str, *, event_name: str, new_status: str,
                       start_date: str, start_time: str, end_date: str, end_time: str, venue: str,
                       reason: Optional[str] = None):
    subject = f"Update: '{event_name}' is {new_status}"
    badge_color = {
        "Approved": "#2e7d32",
        "Pending": "#ef6c00",
        "Rejected": "#c62828",
        "Cancelled": "#c62828"
    }.get(new_status, "#555")
    reason_html = f"<p><strong>Notes:</strong> {escape(reason)}</p>" if reason else ""
    html = f"""
    <div style="font-family:Arial,sans-serif">
      <h2>Status update: <span style="color:{badge_color}">{escape(new_status)}</span></h2>
      <p><strong>Event:</strong> {escape(event_name)}<br>
         <strong>Venue:</strong> {escape(venue or '-') }<br>
         <strong>When:</strong> {escape(start_date)} {escape(start_time or '')} – {escape(end_date or start_date)} {escape(end_time or '')}</p>
      {reason_html}
      <p>If you have questions, reply to this email.</p>
      <hr>
      <p style="color:#888;font-size:12px">Sunshine Coast Council – Event Permit Prototype</p>
    </div>
    """
    text = f"""Status update: {new_status}
Event: {event_name}
Venue: {venue or '-'}
When: {start_date} {start_time or ''} – {end_date or start_date} {end_time or ''}
{('Notes: ' + reason) if reason else ''}
"""
    return _send_email(to_addr, subject, html, text)

# simple HTML escape util
def escape(s):
    if s is None: return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))
