"""Google Sheets backup: sync teachers, slots, and bookings."""
import os
import json
import logging

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SPREADSHEET_ID = "1bOLqLKiDo-Kk9VK5DKz_5tvRs5SAEGwCOJQkZEJTj3A"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

_gs_client = None


def _get_client():
    global _gs_client
    if _gs_client is not None:
        return _gs_client

    key_data = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_data:
        logger.warning("GOOGLE_SERVICE_ACCOUNT_JSON not set — sheets backup disabled")
        return None

    info = json.loads(key_data)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    _gs_client = gspread.authorize(creds)
    return _gs_client


def _get_or_create_sheet(client, name, headers):
    """Get worksheet by name, or create it with headers."""
    try:
        sheet = client.open_by_key(SPREADSHEET_ID)
    except Exception:
        logger.error("Cannot open spreadsheet %s", SPREADSHEET_ID)
        return None

    try:
        ws = sheet.worksheet(name)
        return ws
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=name, rows=100, cols=len(headers))
        ws.append_row(headers)
        return ws


def sync_teacher(telegram_id, name, username=""):
    """Add or update a teacher row in Google Sheets."""
    try:
        client = _get_client()
        ws = _get_or_create_sheet(client, "O'qituvchilar", ["ID", "Ism", "Username", "Telegram ID"])
        if ws is None:
            return

        # Check if teacher already exists
        records = ws.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("Telegram ID", "")) == str(telegram_id):
                ws.update(f"A{i+2}:D{i+2}", [[i+1, name, username, str(telegram_id)]])
                return

        # Add new row
        new_id = len(records) + 1
        ws.append_row([new_id, name, username, str(telegram_id)])
        logger.info("Teacher synced to sheets: %s", name)
    except Exception as e:
        logger.error("Failed to sync teacher to sheets: %s", e)


def sync_slot(slot_id, teacher_name, date_str, time_str, status):
    """Add a new slot row to Google Sheets."""
    try:
        client = _get_client()
        ws = _get_or_create_sheet(client, "Slotlar", ["ID", "O'qituvchi", "Sana", "Vaqt", "Holati"])
        if ws is None:
            return

        ws.append_row([slot_id, teacher_name, date_str, time_str, status])
        logger.info("Slot synced to sheets: %s %s %s", teacher_name, date_str, time_str)
    except Exception as e:
        logger.error("Failed to sync slot to sheets: %s", e)


def sync_booking(booking_id, student_name, teacher_name, date_str, time_str, status):
    """Add or update a booking row in Google Sheets."""
    try:
        client = _get_client()
        ws = _get_or_create_sheet(
            client,
            "Bandlovlar",
            ["ID", "O'quvchi", "O'qituvchi", "Sana", "Vaqt", "Holati", "Vaqt"],
        )
        if ws is None:
            return

        records = ws.get_all_records()
        for i, row in enumerate(records):
            if row.get("ID") == booking_id:
                ws.update(
                    f"A{i+2}:G{i+2}",
                    [[booking_id, student_name, teacher_name, date_str, time_str, status, ""]],
                )
                return

        ws.append_row([booking_id, student_name, teacher_name, date_str, time_str, status, ""])
        logger.info("Booking synced to sheets: %s -> %s", student_name, teacher_name)
    except Exception as e:
        logger.error("Failed to sync booking to sheets: %s", e)
