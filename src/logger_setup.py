# ============================================================
# logger_setup.py — Configure Logging to File + Console
# Email Automation & Reminder System
# ============================================================

import logging
import os
from datetime import datetime
from src.config import LOGS_DIR, LOG_FILE


def setup_logger(level=logging.INFO):
    """
    Set up root logger to write to both console and a log file.
    Log file is named with today's date for easy organization.

    Args:
        level: logging level (default: INFO)
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Create a dated log file name, e.g. logs/email_log_2024-12-20.txt
    dated_log_file = LOG_FILE.replace(".txt", f"_{datetime.now().strftime('%Y-%m-%d')}.txt")

    # ── Root logger ────────────────────────────────────────
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # ── Formatter ──────────────────────────────────────────
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Console handler ────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(fmt)

    # ── File handler ───────────────────────────────────────
    file_handler = logging.FileHandler(dated_log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)   # Log everything to file
    file_handler.setFormatter(fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"📋 Logger initialized. Log file: {dated_log_file}")
    return logger
