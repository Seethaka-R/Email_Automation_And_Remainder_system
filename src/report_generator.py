# ============================================================
# report_generator.py - CSV Report & Summary Generation
# Email Automation & Reminder System
# ============================================================

import csv
import logging
import os
from datetime import datetime

from src.config import OUTPUTS_DIR, REPORT_FILE

logger = logging.getLogger(__name__)
active_report_file = REPORT_FILE

# CSV columns for the output report
REPORT_COLUMNS = [
    "timestamp", "reminder_id", "contact_name", "to_email",
    "reminder_type", "subject", "send_datetime",
    "status", "attempts", "message"
]


def _write_header_if_needed(file_path: str):
    """Create a report file with headers when it does not exist yet."""
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
            writer.writeheader()


def _fallback_report_file() -> str:
    """Return a unique report filename for this run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUTS_DIR, f"email_report_{timestamp}.csv")


def get_report_file() -> str:
    """Return the report file currently being written to."""
    return active_report_file


def init_report():
    """
    Create the output directory and write CSV header if the file doesn't exist.
    Call this once at startup.
    """
    global active_report_file

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    active_report_file = REPORT_FILE

    try:
        _write_header_if_needed(active_report_file)
        logger.info(f"Report initialized: {active_report_file}")
    except PermissionError:
        active_report_file = _fallback_report_file()
        _write_header_if_needed(active_report_file)
        logger.warning(
            "Could not write to %s. It may be open in Excel. "
            "Using %s for this run instead.",
            REPORT_FILE,
            active_report_file,
        )


def append_to_report(result: dict):
    """
    Append a single email result row to the CSV report.

    Args:
        result: dict from send_email() enriched with reminder metadata
    """
    global active_report_file

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reminder_id": result.get("reminder_id", "N/A"),
        "contact_name": result.get("contact_name", "N/A"),
        "to_email": result.get("to_email", "N/A"),
        "reminder_type": result.get("reminder_type", "N/A"),
        "subject": result.get("subject", "N/A"),
        "send_datetime": result.get("send_datetime", "N/A"),
        "status": result.get("status", "unknown"),
        "attempts": result.get("attempts", 0),
        "message": result.get("message", ""),
    }

    try:
        with open(active_report_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
            writer.writerow(row)
    except PermissionError:
        locked_file = active_report_file
        active_report_file = _fallback_report_file()
        _write_header_if_needed(active_report_file)
        logger.warning(
            "Could not append to %s. It may be open in Excel. "
            "Continuing with %s.",
            locked_file,
            active_report_file,
        )
        with open(active_report_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
            writer.writerow(row)

    logger.debug(f"Report row appended: {row['reminder_id']} -> {row['status']}")


def generate_summary(results: list) -> dict:
    """
    Generate a summary from a list of result dicts.

    Returns a dict with total, sent, failed, dry_run counts and success rate.
    """
    total = len(results)
    sent = sum(1 for r in results if r["status"] == "sent")
    dry_run = sum(1 for r in results if r["status"] == "dry_run")
    failed = sum(1 for r in results if r["status"] == "failed")
    success_rate = round(((sent + dry_run) / total * 100), 2) if total > 0 else 0

    summary = {
        "total": total,
        "sent": sent,
        "dry_run": dry_run,
        "failed": failed,
        "success_rate": success_rate,
    }
    return summary


def print_summary(summary: dict):
    """Pretty-print the final summary to terminal."""
    print("\n" + "=" * 55)
    print("       EMAIL AUTOMATION - FINAL REPORT")
    print("=" * 55)
    print(f"  Total Processed  : {summary['total']}")
    print(f"  Sent             : {summary['sent']}")
    print(f"  Dry-Run          : {summary['dry_run']}")
    print(f"  Failed           : {summary['failed']}")
    print(f"  Success Rate     : {summary['success_rate']}%")
    print("=" * 55)
    print(f"  Report saved to  : {os.path.relpath(active_report_file)}")
    print("=" * 55 + "\n")
