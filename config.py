import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
# SQLite (dev) by default; override with DATABASE_URL for cloud (e.g. Postgres)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'events.db'}")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

# config.py
GMAPS_API_KEY = os.getenv("GMAPS_API_KEY", "")  # optional

# --- Email config (Gmail SMTP) ---
EMAIL_SMTP_HOST = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

# The visible "From" line in emails
EMAIL_FROM = "Sunshine Coast Council <no-reply@scc.example>"

# Use environment variables for secrets:
#   setx EMAIL_USER "youremail@gmail.com"
#   setx EMAIL_PASS "your_app_password"
import os
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
