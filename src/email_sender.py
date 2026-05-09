# ============================================================
# email_sender.py — SMTP Email Sending with Dry-Run Mode
# Email Automation & Reminder System
# ============================================================

import smtplib
import time
import logging
from email.message import EmailMessage
from src.config import (
    SMTP_HOST, SMTP_PORT, SENDER_EMAIL,
    SENDER_PASSWORD, SENDER_NAME,
    DRY_RUN, MAX_RETRIES, RETRY_DELAY
)

logger = logging.getLogger(__name__)


def create_email_message(to_email: str, subject: str, body: str) -> EmailMessage:
    """
    Build a standard EmailMessage object.

    Args:
        to_email : recipient email address
        subject  : email subject line
        body     : email body text

    Returns:
        EmailMessage ready to send
    """
    msg = EmailMessage()
    msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def send_email(to_email: str, subject: str, body: str,
               contact_name: str = "Recipient") -> dict:
    """
    Send a single email. Automatically uses DRY_RUN mode if configured.
    Retries up to MAX_RETRIES times on failure.

    Returns:
        dict with keys: status ("sent"/"failed"/"dry_run"), message, attempts
    """
    result = {
        "to_email":     to_email,
        "contact_name": contact_name,
        "subject":      subject,
        "status":       "",
        "message":      "",
        "attempts":     0,
    }

    # ── DRY RUN MODE (safe testing) ────────────────────────
    if DRY_RUN:
        logger.info(f"🧪 [DRY RUN] Would send to: {contact_name} <{to_email}>")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Body preview: {body[:100].strip()}...")
        result["status"]  = "dry_run"
        result["message"] = "Email simulated in dry-run mode. Not actually sent."
        return result

    # ── REAL EMAIL SENDING (with retries) ──────────────────
    msg = create_email_message(to_email, subject, body)

    for attempt in range(1, MAX_RETRIES + 1):
        result["attempts"] = attempt
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls()          # Encrypt the connection
                server.ehlo()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)

            logger.info(f"✅ Email sent to {contact_name} <{to_email}> "
                        f"(attempt {attempt})")
            result["status"]  = "sent"
            result["message"] = f"Email delivered successfully on attempt {attempt}."
            return result

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ SMTP Authentication failed. Check SENDER_EMAIL and SENDER_PASSWORD.")
            result["status"]  = "failed"
            result["message"] = "SMTP authentication error. Check your credentials."
            return result   # No point retrying auth errors

        except smtplib.SMTPRecipientsRefused:
            logger.warning(f"⚠️  Recipient refused: {to_email}")
            result["status"]  = "failed"
            result["message"] = f"Recipient address refused: {to_email}"
            return result

        except (smtplib.SMTPException, ConnectionError, OSError) as e:
            logger.warning(f"⚠️  Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                logger.info(f"   Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"❌ All {MAX_RETRIES} attempts failed for {to_email}.")
                result["status"]  = "failed"
                result["message"] = f"Failed after {MAX_RETRIES} attempts. Last error: {e}"

    return result


def send_bulk_emails(email_jobs: list) -> list:
    """
    Send multiple emails from a list of job dicts.

    Each job dict must have: to_email, subject, body, contact_name

    Returns list of result dicts.
    """
    results = []
    total = len(email_jobs)
    logger.info(f"📧 Starting bulk send: {total} email(s) queued.")

    for i, job in enumerate(email_jobs, 1):
        logger.info(f"--- [{i}/{total}] Processing: {job.get('contact_name')} ---")
        result = send_email(
            to_email=job["to_email"],
            subject=job["subject"],
            body=job["body"],
            contact_name=job.get("contact_name", "Recipient"),
        )
        results.append(result)

        # Small delay between emails to avoid rate limiting
        if not DRY_RUN and i < total:
            time.sleep(1)

    sent    = sum(1 for r in results if r["status"] == "sent")
    dry     = sum(1 for r in results if r["status"] == "dry_run")
    failed  = sum(1 for r in results if r["status"] == "failed")
    logger.info(f"📊 Bulk send complete — Sent: {sent} | Dry-Run: {dry} | Failed: {failed}")
    return results
