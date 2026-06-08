"""Google Sheets sync — export (backup) and import (startup restore)."""
import json
import os
import logging

logger = logging.getLogger(__name__)

SHEET_ID = "1bOLqLKiDo-Kk9VK5DKz_5tvRs5SAEGwCOJQkZEJTj3A"

CRED_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")


def _get_client():
    """Get gspread client from env var or file."""
    if not CRED_JSON:
        logger.warning("GOOGLE_SERVICE_ACCOUNT_JSON not set")
        return None
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = json.loads(CRED_JSON)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        return gspread.authorize(creds)
    except Exception as e:
        logger.error("gspread auth failed: %s", e)
        return None


def _get_sheet():
    client = _get_client()
    if not client:
        return None
    try:
        return client.open_by_key(SHEET_ID)
    except Exception as e:
        logger.error("Cannot open sheet %s: %s", SHEET_ID, e)
        return None


def _ensure_headers(ws, headers):
    """Ensure first row has the right headers."""
    try:
        existing = ws.row_values(1)
    except Exception:
        existing = []
    if not existing or existing != headers:
        if not existing:
            ws.insert_row(headers, 1)
        else:
            ws.update("A1:Z1", [headers])


def sync_teacher(telegram_id, name, username=""):
    sh = _get_sheet()
    if not sh:
        return
    try:
        ws = sh.worksheet("O'qituvchilar")
    except Exception:
        ws = sh.add_worksheet(title="O'qituvchilar", rows=100, cols=10)
    _ensure_headers(ws, ["Telegram ID", "Ism", "Username", "Qo'shilgan sana"])
    ws.append_row([str(telegram_id), name, username or "", ""])


def sync_slot(slot_id, teacher_name, date, time, status):
    sh = _get_sheet()
    if not sh:
        return
    try:
        ws = sh.worksheet("Slotlar")
    except Exception:
        ws = sh.add_worksheet(title="Slotlar", rows=200, cols=10)
    _ensure_headers(ws, ["Slot ID", "O'qituvchi", "Sana", "Vaqt", "Holati"])
    ws.append_row([slot_id, teacher_name, date, time, status])


def sync_booking(booking_id, student_name, teacher_name, date, time, status):
    sh = _get_sheet()
    if not sh:
        return
    try:
        ws = sh.worksheet("Bandlovlar")
    except Exception:
        ws = sh.add_worksheet(title="Bandlovlar", rows=500, cols=10)
    _ensure_headers(ws, ["Booking ID", "O'quvchi", "O'qituvchi", "Sana", "Vaqt", "Holati"])
    ws.append_row([str(booking_id), student_name, teacher_name, date, time, status])


# ─── Startup Import ───────────────────────────────────

def load_from_sheets():
    """On startup: read teachers & slots from Google Sheets into SQLite.
    Returns (teacher_count, slot_count)."""
    sh = _get_sheet()
    if not sh:
        return 0, 0

    import sqlite3
    from db import DB

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    t_count = 0
    s_count = 0

    # --- Load teachers ---
    try:
        ws = sh.worksheet("O'qituvchilar")
        rows = ws.get_all_records()
        for r in rows:
            tid = str(r.get("Telegram ID", "")).strip()
            name = str(r.get("Ism", "")).strip()
            username = str(r.get("Username", "")).strip()
            if tid and name:
                conn.execute(
                    "INSERT OR IGNORE INTO teachers (telegram_id, name, username) VALUES (?, ?, ?)",
                    (int(tid), name, username),
                )
                t_count += 1
        conn.commit()
    except Exception as e:
        logger.warning("load_from_sheets — teachers: %s", e)

    # --- Load slots ---
    try:
        ws = sh.worksheet("Slotlar")
        rows = ws.get_all_records()
        for r in rows:
            teacher_name = str(r.get("O'qituvchi", "")).strip()
            date = str(r.get("Sana", "")).strip()
            time = str(r.get("Vaqt", "")).strip()
            status = str(r.get("Holati", "available")).strip()

            if not teacher_name or not date or not time:
                continue

            # Find teacher by name
            teacher = conn.execute(
                "SELECT id FROM teachers WHERE name = ?", (teacher_name,)
            ).fetchone()
            if not teacher:
                continue

            # Insert slot if not exists
            existing = conn.execute(
                "SELECT id FROM slots WHERE teacher_id = ? AND date = ? AND time = ?",
                (teacher["id"], date, time),
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO slots (teacher_id, date, time, status) VALUES (?, ?, ?, ?)",
                    (teacher["id"], date, time, status),
                )
                s_count += 1
        conn.commit()
    except Exception as e:
        logger.warning("load_from_sheets — slots: %s", e)

    conn.close()
    return t_count, s_count
