# ============================================================
# config.py — Configuration & Environment Variable Loader
# Email Automation & Reminder System
# ============================================================

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Email / SMTP Settings ──────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")        # Never hardcode!
SENDER_NAME = os.getenv("SENDER_NAME", "Email Automation System")

# ── File Paths ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.csv")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.csv")
REPORT_FILE = os.path.join(OUTPUTS_DIR, "email_report.csv")
LOG_FILE = os.path.join(LOGS_DIR, "email_log.txt")

# ── App Settings ───────────────────────────────────────────
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"   # Safe mode by default
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))             # seconds

# Template name → file mapping
TEMPLATE_MAP = {
    "meeting_reminder":  "meeting_reminder.txt",
    "deadline_reminder": "deadline_reminder.txt",
    "followup_reminder": "followup_reminder.txt",
    "task_reminder":     "task_reminder.txt",
    "payment_reminder":  "payment_reminder.txt",
    "webinar_reminder":  "webinar_reminder.txt",
}
