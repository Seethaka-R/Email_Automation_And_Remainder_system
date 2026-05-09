#!/usr/bin/env python3
# ============================================================
# main.py — Entry Point for Email Automation & Reminder System
#
# Usage:
#   python main.py                    → Dry-run (safe, no real emails)
#   python main.py --send             → Send real emails (set .env first!)
#   python main.py --schedule         → Start live scheduler (dry-run)
#   python main.py --schedule --send  → Start live scheduler (real emails)
#   python main.py --all              → Process ALL reminders now (dry-run)
#   python main.py --all --send       → Process ALL reminders now (real)
# ============================================================

import sys
import os
import argparse
import logging

# ── Make sure src/ is importable ──────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.logger_setup import setup_logger
from src.contact_loader import load_contacts
from src.reminder_loader import load_reminders
from src.template_engine import load_template, personalize_template, build_email_context
from src.email_sender import send_email, send_bulk_emails
from src.report_generator import (
    init_report,
    append_to_report,
    generate_summary,
    print_summary,
)
from src.config import DRY_RUN


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="📧 Email Automation & Reminder System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Dry-run: simulate all reminders
  python main.py --send             # Send real emails (configure .env first)
  python main.py --schedule         # Live scheduler in dry-run mode
  python main.py --all --send       # Process all reminders + send real emails
        """
    )
    parser.add_argument("--send",     action="store_true", help="Enable real email sending")
    parser.add_argument("--schedule", action="store_true", help="Start live minute-by-minute scheduler")
    parser.add_argument("--all",      action="store_true", help="Process all reminders immediately")
    return parser.parse_args()


def process_all_reminders(contacts_df, reminders_df) -> list:
    """
    Process every reminder in the CSV immediately.
    Great for batch testing or end-of-day runs.
    """
    logger = logging.getLogger(__name__)
    email_jobs = []
    skipped = 0

    for _, reminder in reminders_df.iterrows():
        from src.contact_loader import get_contact_by_id
        contact = get_contact_by_id(int(reminder["contact_id"]), contacts_df)

        if not contact:
            logger.warning(f"⚠️  Skipping reminder {reminder['reminder_id']}: contact not found.")
            skipped += 1
            continue

        try:
            template = load_template(reminder["message_key"])
            context  = build_email_context(contact, reminder.to_dict())
            subject, body = personalize_template(template, context)

            email_jobs.append({
                "to_email":      contact["email"],
                "subject":       subject,
                "body":          body,
                "contact_name":  contact["name"],
                "reminder_id":   reminder["reminder_id"],
                "reminder_type": reminder["reminder_type"],
                "send_datetime": str(reminder["send_datetime"]),
            })
        except Exception as e:
            logger.error(f"❌ Error building job for {reminder['reminder_id']}: {e}")
            skipped += 1

    logger.info(f"📬 {len(email_jobs)} email jobs built. {skipped} skipped.")

    # Send all emails
    results = []
    for job in email_jobs:
        result = send_email(
            to_email=job["to_email"],
            subject=job["subject"],
            body=job["body"],
            contact_name=job["contact_name"],
        )
        result["reminder_id"]   = job["reminder_id"]
        result["reminder_type"] = job["reminder_type"]
        result["send_datetime"] = job["send_datetime"]
        append_to_report(result)
        results.append(result)

    return results


def main():
    args = parse_args()

    # Override DRY_RUN env var if --send flag is passed
    if args.send:
        os.environ["DRY_RUN"] = "false"
        # Reload config after env change
        import src.config as cfg
        cfg.DRY_RUN = False
        import src.email_sender as es
        es.DRY_RUN = False

    # ── Set up logging ─────────────────────────────────────
    logger = setup_logger()

    # ── Print banner ───────────────────────────────────────
    print("\n" + "=" * 55)
    print("  📧  EMAIL AUTOMATION & REMINDER SYSTEM")
    print("      Built with Python | Student Project")
    print("=" * 55)
    mode = "🚀 LIVE SEND" if args.send else "🧪 DRY RUN (safe mode)"
    print(f"  Mode: {mode}")
    print("=" * 55 + "\n")

    # ── Load data ──────────────────────────────────────────
    logger.info("📂 Loading contacts and reminders...")
    contacts_df  = load_contacts()
    reminders_df = load_reminders()

    # ── Initialize report file ─────────────────────────────
    init_report()

    # ── Run mode selection ─────────────────────────────────
    if args.schedule:
        # Live scheduler — checks every minute for due reminders
        from src.scheduler import start_scheduler
        start_scheduler(contacts_df, reminders_df)

    else:
        # Batch mode — process all reminders now
        logger.info("📨 Running in batch mode: processing all reminders now...")
        results = process_all_reminders(contacts_df, reminders_df)

        # ── Summary ────────────────────────────────────────
        summary = generate_summary(results)
        print_summary(summary)
        logger.info("✅ All done. Check outputs/email_report.csv for the full report.")


if __name__ == "__main__":
    main()
