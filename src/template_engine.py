# ============================================================
# template_engine.py — Load & Personalize Email Templates
# Email Automation & Reminder System
# ============================================================

import os
import logging
from src.config import TEMPLATES_DIR, TEMPLATE_MAP

logger = logging.getLogger(__name__)


def load_template(message_key: str) -> str:
    """
    Load a raw email template from the templates/ folder.

    Args:
        message_key: key from TEMPLATE_MAP (e.g. "meeting_reminder")

    Returns:
        Raw template string with placeholders like {name}, {subject}
    """
    filename = TEMPLATE_MAP.get(message_key)
    if not filename:
        raise ValueError(f"❌ Unknown template key: '{message_key}'. "
                         f"Valid keys: {list(TEMPLATE_MAP.keys())}")

    filepath = os.path.join(TEMPLATES_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        logger.debug(f"📄 Loaded template: {filename}")
        return content
    except FileNotFoundError:
        logger.error(f"❌ Template file not found: {filepath}")
        raise


def personalize_template(template: str, context: dict) -> tuple:
    """
    Replace all {placeholder} tokens in the template with real values.

    Args:
        template: raw template string
        context:  dict of values  e.g. {"name": "Arjun", "subject": "..."}

    Returns:
        (subject_line, body_text) as a tuple
    """
    try:
        # Fill all placeholders
        filled = template.format(**context)

        # Split subject from body (first line = subject after "Subject: ")
        lines = filled.strip().splitlines()
        subject_line = ""
        body_lines = []

        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject_line = line.replace("Subject:", "").replace("subject:", "").strip()
            else:
                body_lines.append(line)

        body_text = "\n".join(body_lines).strip()
        logger.debug(f"✅ Template personalized for: {context.get('name', 'Unknown')}")
        return subject_line, body_text

    except KeyError as e:
        logger.error(f"❌ Missing placeholder in template context: {e}")
        raise


def build_email_context(contact: dict, reminder: dict) -> dict:
    """
    Merge contact and reminder data into a single context dict
    used for template personalization.
    """
    return {
        "name":        contact.get("name", "Team Member"),
        "email":       contact.get("email", ""),
        "department":  contact.get("department", "N/A"),
        "role":        contact.get("role", "N/A"),
        "phone":       contact.get("phone", "N/A"),
        "subject":     reminder.get("subject", "Reminder"),
        "send_date":   reminder.get("send_date", ""),
        "send_time":   reminder.get("send_time", ""),
        "reminder_type": reminder.get("reminder_type", "general"),
        "priority":    reminder.get("priority", "medium"),
        "reminder_id": reminder.get("reminder_id", ""),
    }
