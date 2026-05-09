# ============================================================
# reminder_loader.py — Read & Parse Reminders from CSV
# Email Automation & Reminder System
# ============================================================

import pandas as pd
import logging
from datetime import datetime
from src.config import REMINDERS_FILE

logger = logging.getLogger(__name__)


def load_reminders() -> pd.DataFrame:
    """
    Load reminders from CSV file.

    Expected columns:
      reminder_id, contact_id, reminder_type, subject,
      send_date, send_time, priority, message_key
    """
    try:
        df = pd.read_csv(REMINDERS_FILE)
        logger.info(f"✅ Loaded {len(df)} reminders from {REMINDERS_FILE}")

        # ── Validate required columns ──────────────────────
        required_cols = ["reminder_id", "contact_id", "subject",
                         "send_date", "send_time", "message_key"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in reminders.csv: {missing}")

        # ── Parse datetime ─────────────────────────────────
        df["send_datetime"] = pd.to_datetime(
            df["send_date"].astype(str) + " " + df["send_time"].astype(str),
            errors="coerce"
        )

        # Warn about any un-parseable rows
        bad_dates = df[df["send_datetime"].isna()]
        if not bad_dates.empty:
            logger.warning(f"⚠️  {len(bad_dates)} reminders have invalid dates and will be skipped.")
            df = df.dropna(subset=["send_datetime"])

        df.sort_values("send_datetime", inplace=True)
        logger.info(f"✅ {len(df)} valid reminders loaded and sorted by schedule time.")
        return df

    except FileNotFoundError:
        logger.error(f"❌ reminders.csv not found at: {REMINDERS_FILE}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading reminders: {e}")
        raise


def get_due_reminders(reminders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter reminders that are due NOW (within the current minute).
    Used by the live scheduler.
    """
    now = datetime.now().replace(second=0, microsecond=0)
    due = reminders_df[reminders_df["send_datetime"] == now]
    if not due.empty:
        logger.info(f"🔔 {len(due)} reminder(s) due at {now.strftime('%H:%M')}")
    return due
