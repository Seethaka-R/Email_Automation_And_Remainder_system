# ============================================================
# contact_loader.py — Read & Validate Contacts from CSV
# Email Automation & Reminder System
# ============================================================

import pandas as pd
import logging
from src.config import CONTACTS_FILE

logger = logging.getLogger(__name__)


def load_contacts() -> pd.DataFrame:
    """
    Load contacts from the CSV file.
    Returns a cleaned DataFrame with all contacts.

    Expected columns: id, name, email, department, role, phone
    """
    try:
        df = pd.read_csv(CONTACTS_FILE)
        logger.info(f"✅ Loaded {len(df)} contacts from {CONTACTS_FILE}")

        # ── Validate required columns ──────────────────────
        required_cols = ["id", "name", "email", "department", "role"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in contacts.csv: {missing}")

        # ── Clean data ─────────────────────────────────────
        df["email"] = df["email"].str.strip().str.lower()
        df["name"]  = df["name"].str.strip().str.title()
        df.dropna(subset=["email", "name"], inplace=True)

        # ── Validate email format (basic check) ────────────
        valid_mask = df["email"].str.contains(r"^[\w\.-]+@[\w\.-]+\.\w+$", regex=True)
        invalid = df[~valid_mask]
        if not invalid.empty:
            logger.warning(f"⚠️  Skipping {len(invalid)} contacts with invalid email addresses.")
            df = df[valid_mask]

        logger.info(f"✅ {len(df)} valid contacts ready for processing.")
        return df

    except FileNotFoundError:
        logger.error(f"❌ contacts.csv not found at: {CONTACTS_FILE}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading contacts: {e}")
        raise


def get_contact_by_id(contact_id: int, contacts_df: pd.DataFrame) -> dict:
    """
    Return a single contact as a dict by their ID.
    Returns None if not found.
    """
    match = contacts_df[contacts_df["id"] == contact_id]
    if match.empty:
        logger.warning(f"⚠️  No contact found with ID: {contact_id}")
        return None
    return match.iloc[0].to_dict()
