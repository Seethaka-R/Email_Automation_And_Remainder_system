# ============================================================
# scheduler.py — Reminder Scheduling with the schedule library
# Email Automation & Reminder System
# ============================================================

import schedule
import time
import logging
from datetime import datetime
import pandas as pd

from src.reminder_loader import get_due_reminders
from src.contact_loader import get_contact_by_id
from src.template_engine import load_template, personalize_template, build_email_context
from src.email_sender import send_email
from src.report_generator import append_to_report

logger = logging.getLogger(__name__)

# Global references set when scheduler starts
_contacts_df = None
_reminders_df = None


def process_due_reminders():
    """
    Called every minute by the scheduler.
    Checks for reminders due NOW and sends the emails.
    """
    global _contacts_df, _reminders_df

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    logger.debug(f"🕐 Scheduler tick — checking reminders at {now}")

    due = get_due_reminders(_reminders_df)
    if due.empty:
        return

    for _, reminder in due.iterrows():
        contact = get_contact_by_id(int(reminder["contact_id"]), _contacts_df)
        if not contact:
            logger.warning(f"⚠️  Contact ID {reminder['contact_id']} not found. Skipping.")
            continue

        try:
            template = load_template(reminder["message_key"])
            context  = build_email_context(contact, reminder.to_dict())
            subject, body = personalize_template(template, context)

            result = send_email(
                to_email=contact["email"],
                subject=subject,
                body=body,
                contact_name=contact["name"]
            )
            result["reminder_id"]   = reminder["reminder_id"]
            result["reminder_type"] = reminder["reminder_type"]
            result["send_datetime"] = str(reminder["send_datetime"])
            append_to_report(result)

        except Exception as e:
            logger.error(f"❌ Failed to process reminder {reminder['reminder_id']}: {e}")


def start_scheduler(contacts_df: pd.DataFrame, reminders_df: pd.DataFrame):
    """
    Start the live scheduler. Runs every minute and checks for due reminders.

    Args:
        contacts_df : loaded contacts DataFrame
        reminders_df: loaded reminders DataFrame
    """
    global _contacts_df, _reminders_df
    _contacts_df  = contacts_df
    _reminders_df = reminders_df

    logger.info("⏰ Scheduler started. Checking every minute for due reminders...")
    logger.info("   Press Ctrl+C to stop.\n")

    schedule.every(1).minutes.do(process_due_reminders)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)   # Check schedule twice a minute
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped by user (Ctrl+C).")
