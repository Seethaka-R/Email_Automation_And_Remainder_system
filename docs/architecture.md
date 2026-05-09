# 📐 Architecture — Email Automation & Reminder System

## System Overview

This project follows a **Pipeline Architecture** pattern:

```
Input → Process → Output
```

Each stage is independent and communicates through simple data structures (DataFrames, dicts, lists).

---

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Central config — all paths, SMTP settings, env var loading |
| `contact_loader.py` | Read, validate, and clean contacts CSV |
| `reminder_loader.py` | Read, parse, and sort reminders CSV |
| `template_engine.py` | Load template files, fill placeholders with contact/reminder data |
| `email_sender.py` | Send emails via SMTP (or simulate in dry-run mode), with retries |
| `scheduler.py` | Run minute-by-minute and trigger `email_sender` for due reminders |
| `report_generator.py` | Write results to CSV report and print terminal summary |
| `logger_setup.py` | Configure logging to console + timestamped log file |

---

## Data Flow

```
contacts.csv
     │
     ▼
contact_loader.py ──► contacts DataFrame
                              │
                              │ (merge by contact_id)
                              │
reminders.csv                 │
     │                        │
     ▼                        │
reminder_loader.py ──► reminders DataFrame
                              │
                              │ (for each reminder)
                              ▼
                      template_engine.py
                              │ (load template + fill {placeholders})
                              ▼
                      personalized (subject, body)
                              │
                              ▼
                      email_sender.py
                        ┌─────┴─────┐
                     DRY_RUN=true  DRY_RUN=false
                        │              │
                   simulate         SMTP send
                        │              │
                        └─────┬─────┘
                              ▼
                      result dict {status, message, attempts}
                              │
                              ▼
                      report_generator.py ──► outputs/email_report.csv
                              │
                              ▼
                      logs/email_log_YYYY-MM-DD.txt
```

---

## Scheduling Architecture

```
main.py
   │
   ├── --schedule flag
   │       │
   │       ▼
   │   scheduler.py
   │       │
   │       ├── schedule.every(1).minutes
   │       │       │
   │       │       ▼ (every minute)
   │       │   get_due_reminders()
   │       │       │
   │       │       ▼ (if reminders due now)
   │       │   process_due_reminders()
   │       │       │
   │       │       ▼
   │       │   email_sender.send_email()
   │       │
   │       └── Ctrl+C → graceful stop
   │
   └── (no --schedule flag)
           │
           ▼
       process_all_reminders() → immediate batch processing
```

---

## Security Design

- **No hardcoded credentials** — All sensitive values in `.env`
- **`.env` in `.gitignore`** — Credentials never reach GitHub
- **`.env.example`** — Safe template committed to repo for guidance
- **DRY_RUN=true by default** — System is safe out-of-the-box
- **STARTTLS encryption** — All SMTP connections encrypted

---

## Error Handling Strategy

| Error Type | Handling |
|---|---|
| File not found | `FileNotFoundError` logged, program exits with message |
| Invalid CSV column | `ValueError` logged with exact missing columns |
| Invalid email format | Row skipped, warning logged |
| SMTP auth failure | Immediate fail, no retry (wrong credentials won't fix themselves) |
| Network timeout | Retry up to `MAX_RETRIES` times with `RETRY_DELAY` seconds between |
| Missing template key | `ValueError` raised with valid key list shown |
| Missing placeholder in template | `KeyError` logged, reminder skipped |
