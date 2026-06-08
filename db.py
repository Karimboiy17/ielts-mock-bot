import sqlite3
import os
import logging
from datetime import date, timedelta

DB = "bookings.db"
logger = logging.getLogger(__name__)


def _sheets(*args, **kwargs):
    """Lazy import to avoid crash if gspread not installed."""
    try:
        from sheets_backup import sync_teacher, sync_slot, sync_booking
        return {"sync_teacher": sync_teacher, "sync_slot": sync_slot, "sync_booking": sync_booking}
    except ImportError:
        return {}


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'uz',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_id INTEGER NOT NULL,
            student_telegram_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_username TEXT,
            status TEXT DEFAULT 'pending',
            payment_photo_id TEXT,
            payment_status TEXT DEFAULT 'none',
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (slot_id) REFERENCES slots(id)
        );

        CREATE TABLE IF NOT EXISTS recurring_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_telegram_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            time TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(teacher_telegram_id, day_of_week, time)
        );
    """)
    conn.commit()
    conn.close()


# ─── Language ──────────────────────────────────────────────

def set_language(telegram_id, lang):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO users (telegram_id, language) VALUES (?, ?)",
        (telegram_id, lang),
    )
    conn.commit()
    conn.close()


def get_language(telegram_id):
    conn = get_db()
    row = conn.execute(
        "SELECT language FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    conn.close()
    return row["language"] if row else "uz"


def get_current_payment_for_user(student_telegram_id):
    """Get a payment-pending booking for a student, if they have one."""
    conn = get_db()
    row = conn.execute(
        """
        SELECT b.id, b.slot_id, s.date, s.time, t.name as teacher_name
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        JOIN teachers t ON t.id = s.teacher_id
        WHERE b.student_telegram_id = ? 
          AND b.payment_status = 'waiting_receipt'
        ORDER BY b.id DESC LIMIT 1
        """,
        (student_telegram_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Teacher ──────────────────────────────────────────────

def is_teacher(telegram_id):
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM teachers WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    conn.close()
    return row is not None


def get_teacher_by_id(teacher_db_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM teachers WHERE id = ?", (teacher_db_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_slot(teacher_telegram_id, date, time):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO slots (teacher_id, date, time, status) "
        "VALUES ((SELECT id FROM teachers WHERE telegram_id=?), ?, ?, 'available')",
        (teacher_telegram_id, date, time),
    )
    conn.commit()
    slot_id = cur.lastrowid
    teacher = conn.execute(
        "SELECT name FROM teachers WHERE telegram_id=?", (teacher_telegram_id,)
    ).fetchone()
    conn.close()
    sync = _sheets().get("sync_slot")
    if sync and teacher:
        try:
            sync(str(slot_id), teacher["name"], date, time, "available")
        except Exception as e:
            logger.error("sync_slot failed: %s", e)


def get_teacher_slots(teacher_telegram_id):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT s.id, s.date, s.time, s.status,
               b.student_name, b.student_telegram_id, b.id as booking_id
        FROM slots s
        LEFT JOIN bookings b ON b.slot_id = s.id AND b.status != 'rejected'
        WHERE s.teacher_id = (SELECT id FROM teachers WHERE telegram_id=?)
        ORDER BY s.date, s.time
        """,
        (teacher_telegram_id,),
    ).fetchall()
    conn.close()
    return rows


def remove_slot(slot_id, teacher_telegram_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM slots WHERE id = ? "
        "AND teacher_id = (SELECT id FROM teachers WHERE telegram_id=?) "
        "AND status = 'available'",
        (slot_id, teacher_telegram_id),
    )
    conn.commit()
    conn.close()


# ─── Recurring Patterns ───────────────────────────────────

DAY_NAMES = {
    0: "Dushanba", 1: "Seshanba", 2: "Chorshanba",
    3: "Payshanba", 4: "Juma", 5: "Shanba", 6: "Yakshanba",
}

DAY_NAMES_EN = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday",
}

DAY_NAMES_RU = {
    0: "Понедельник", 1: "Вторник", 2: "Среда",
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье",
}

DAY_NAMES_I18N = {"uz": DAY_NAMES, "en": DAY_NAMES_EN, "ru": DAY_NAMES_RU}


def add_recurring_pattern(teacher_telegram_id, day_of_week, time):
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO recurring_patterns (teacher_telegram_id, day_of_week, time) VALUES (?, ?, ?)",
        (teacher_telegram_id, day_of_week, time),
    )
    conn.commit()
    conn.close()


def get_recurring_patterns(teacher_telegram_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM recurring_patterns WHERE teacher_telegram_id = ? AND active = 1 ORDER BY day_of_week, time",
        (teacher_telegram_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_recurring_pattern(pattern_id, teacher_telegram_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM recurring_patterns WHERE id = ? AND teacher_telegram_id = ?",
        (pattern_id, teacher_telegram_id),
    )
    conn.commit()
    conn.close()


def generate_slots_from_patterns(teacher_telegram_id, weeks=4):
    patterns = get_recurring_patterns(teacher_telegram_id)
    if not patterns:
        return 0

    conn = get_db()
    today = date.today()
    count = 0

    for pattern in patterns:
        target_dow = pattern["day_of_week"]
        t = pattern["time"]

        for week in range(weeks):
            d = today + timedelta(weeks=week)
            days_ahead = target_dow - d.weekday()
            if days_ahead < 0:
                days_ahead += 7
            slot_date = d + timedelta(days=days_ahead)

            slot_date_str = slot_date.strftime("%Y-%m-%d")

            existing = conn.execute(
                "SELECT id FROM slots WHERE teacher_id = (SELECT id FROM teachers WHERE telegram_id=?) AND date = ? AND time = ?",
                (teacher_telegram_id, slot_date_str, t),
            ).fetchone()

            if not existing:
                conn.execute(
                    "INSERT INTO slots (teacher_id, date, time, status) "
                    "VALUES ((SELECT id FROM teachers WHERE telegram_id=?), ?, ?, 'available')",
                    (teacher_telegram_id, slot_date_str, t),
                )
                count += 1

    conn.commit()
    conn.close()
    return count


# ─── Student ──────────────────────────────────────────────

def get_available_slots():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT s.id, s.date, s.time, t.name as teacher_name
        FROM slots s
        JOIN teachers t ON t.id = s.teacher_id
        WHERE s.status = 'available'
        ORDER BY s.date, s.time
        LIMIT 30
        """
    ).fetchall()
    conn.close()
    return rows


def request_booking(slot_id, student_telegram_id, student_name, student_username=""):
    """Student selects a slot → booking created with payment_status='waiting_receipt'."""
    conn = get_db()
    slot = conn.execute(
        "SELECT id, teacher_id FROM slots WHERE id = ? AND status = 'available'",
        (slot_id,),
    ).fetchone()
    if not slot:
        conn.close()
        return None

    conn.execute("UPDATE slots SET status = 'pending' WHERE id = ?", (slot_id,))
    cur = conn.execute(
        "INSERT INTO bookings (slot_id, student_telegram_id, student_name, student_username, status, payment_status) "
        "VALUES (?, ?, ?, ?, 'pending', 'waiting_receipt')",
        (slot_id, student_telegram_id, student_name, student_username),
    )
    booking_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"booking_id": booking_id, "teacher_db_id": slot["teacher_id"]}


def submit_payment_receipt(booking_id, student_telegram_id, photo_file_id):
    """Student sends receipt photo."""
    conn = get_db()
    booking = conn.execute(
        "SELECT id FROM bookings WHERE id = ? AND student_telegram_id = ? AND payment_status = 'waiting_receipt'",
        (booking_id, student_telegram_id),
    ).fetchone()
    if not booking:
        conn.close()
        return None

    conn.execute(
        "UPDATE bookings SET payment_photo_id = ?, payment_status = 'payment_submitted' WHERE id = ?",
        (photo_file_id, booking_id),
    )
    conn.commit()

    # Get full booking info
    info = conn.execute(
        """
        SELECT b.id, b.student_name, b.student_telegram_id, s.date, s.time, t.name as teacher_name, t.telegram_id as teacher_tg
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        JOIN teachers t ON t.id = s.teacher_id
        WHERE b.id = ?
        """,
        (booking_id,),
    ).fetchone()
    conn.close()
    return dict(info) if info else None


def approve_payment(booking_id, admin_telegram_id):
    """Admin approves payment → booking confirmed."""
    conn = get_db()
    row = conn.execute(
        """
        SELECT b.id, b.slot_id, b.student_telegram_id, b.student_name, b.payment_photo_id
        FROM bookings b
        WHERE b.id = ? AND b.payment_status = 'payment_submitted'
        """,
        (booking_id,),
    ).fetchone()
    if not row:
        conn.close()
        return None

    conn.execute("UPDATE slots SET status = 'booked' WHERE id = ?", (row["slot_id"],))
    conn.execute(
        "UPDATE bookings SET status = 'accepted', payment_status = 'payment_approved' WHERE id = ?",
        (booking_id,),
    )

    slot = conn.execute("SELECT date, time FROM slots WHERE id = ?", (row["slot_id"],)).fetchone()
    conn.commit()
    conn.close()

    result = dict(row)
    result["date"] = slot["date"]
    result["time"] = slot["time"]
    return result


def reject_payment(booking_id, admin_telegram_id):
    """Admin rejects payment → slot freed."""
    conn = get_db()
    row = conn.execute(
        """
        SELECT b.id, b.slot_id, b.student_telegram_id, b.student_name, s.date, s.time
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        WHERE b.id = ? AND b.payment_status = 'payment_submitted'
        """,
        (booking_id,),
    ).fetchone()
    if not row:
        conn.close()
        return None

    conn.execute("UPDATE slots SET status = 'available' WHERE id = ?", (row["slot_id"],))
    conn.execute(
        "UPDATE bookings SET status = 'rejected', payment_status = 'payment_rejected' WHERE id = ?",
        (booking_id,),
    )
    conn.commit()
    conn.close()
    return dict(row)


def get_pending_payments():
    """Get all bookings awaiting payment approval."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT b.id, b.student_name, b.student_telegram_id, b.payment_photo_id,
               s.date, s.time, t.name as teacher_name
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        JOIN teachers t ON t.id = s.teacher_id
        WHERE b.payment_status = 'payment_submitted'
        ORDER BY b.id
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def confirm_booking(booking_id, teacher_telegram_id):
    """Teacher accepts → slot and booking become 'booked'."""
    conn = get_db()
    booking = conn.execute(
        """
        SELECT b.id, b.slot_id, b.student_telegram_id, b.student_name,
               s.teacher_id
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        WHERE b.id = ? AND b.status = 'pending'
        """,
        (booking_id,),
    ).fetchone()
    if not booking:
        conn.close()
        return None
    teacher = conn.execute(
        "SELECT id FROM teachers WHERE telegram_id=?", (teacher_telegram_id,)
    ).fetchone()
    if not teacher or teacher["id"] != booking["teacher_id"]:
        conn.close()
        return None

    conn.execute("UPDATE slots SET status = 'booked' WHERE id = ?", (booking["slot_id"],))
    conn.execute("UPDATE bookings SET status = 'accepted' WHERE id = ?", (booking_id,))
    conn.commit()
    slot = conn.execute("SELECT date, time FROM slots WHERE id = ?", (booking["slot_id"],)).fetchone()
    teacher_name = conn.execute(
        "SELECT name FROM teachers WHERE id = ?", (teacher["id"],)
    ).fetchone()
    conn.close()
    sync = _sheets().get("sync_booking")
    if sync and slot and teacher_name:
        try:
            sync(booking_id, booking["student_name"], teacher_name["name"], slot["date"], slot["time"], "Tasdiqlandi")
        except Exception as e:
            logger.error("sync_booking failed: %s", e)
    return {"student_telegram_id": booking["student_telegram_id"], "student_name": booking["student_name"]}


def reject_booking(booking_id, teacher_telegram_id):
    """Teacher rejects → slot freed, booking marked rejected."""
    conn = get_db()
    booking = conn.execute(
        """
        SELECT b.id, b.slot_id, b.student_telegram_id, b.student_name,
               s.teacher_id
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        WHERE b.id = ? AND b.status = 'pending'
        """,
        (booking_id,),
    ).fetchone()
    if not booking:
        conn.close()
        return None
    teacher = conn.execute(
        "SELECT id FROM teachers WHERE telegram_id=?", (teacher_telegram_id,)
    ).fetchone()
    if not teacher or teacher["id"] != booking["teacher_id"]:
        conn.close()
        return None

    conn.execute("UPDATE slots SET status = 'available' WHERE id = ?", (booking["slot_id"],))
    conn.execute("UPDATE bookings SET status = 'rejected' WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return {"student_telegram_id": booking["student_telegram_id"], "student_name": booking["student_name"]}


def get_student_bookings(student_telegram_id):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT b.id, b.slot_id, s.date, s.time, t.name as teacher_name,
               b.status, b.booked_at
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        JOIN teachers t ON t.id = s.teacher_id
        WHERE b.student_telegram_id = ?
        ORDER BY s.date, s.time
        """,
        (student_telegram_id,),
    ).fetchall()
    conn.close()
    return rows


def cancel_booking(booking_id, student_telegram_id):
    conn = get_db()
    booking = conn.execute(
        "SELECT slot_id, status FROM bookings WHERE id = ? AND student_telegram_id = ?",
        (booking_id, student_telegram_id),
    ).fetchone()
    if not booking:
        conn.close()
        return False
    conn.execute("UPDATE slots SET status = 'available' WHERE id = ?", (booking["slot_id"],))
    conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return True


# ─── Admin ────────────────────────────────────────────────

def add_teacher(telegram_id, name, username=""):
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO teachers (telegram_id, name, username) VALUES (?, ?, ?)",
        (telegram_id, name, username),
    )
    conn.commit()
    conn.close()
    sync = _sheets().get("sync_teacher")
    if sync:
        try:
            sync(telegram_id, name, username)
        except Exception as e:
            logger.error("sync_teacher failed: %s", e)


def remove_teacher_db(telegram_id):
    conn = get_db()
    conn.execute("DELETE FROM teachers WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def get_all_bookings():
    conn = get_db()
    rows = conn.execute(
        "SELECT b.id, b.student_name, b.status, b.payment_status, "
        "s.date, s.time, t.name AS teacher_name "
        "FROM bookings b "
        "JOIN slots s ON b.slot_id = s.id "
        "JOIN teachers t ON s.teacher_id = t.id "
        "ORDER BY s.date, s.time"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_teachers():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, telegram_id, name, username FROM teachers ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Google Sheets Sync (startup import) ─────────────────

def sync_from_sheets():
    """On startup: load teachers, slots from Google Sheets into SQLite.
    Returns (teacher_count, slot_count) or (None, None) on error."""
    try:
        from sheets_backup import load_from_sheets
        t_count, s_count = load_from_sheets()
        return t_count, s_count
    except ImportError:
        logger.warning("sheets_backup import failed — skipping sync")
        return None, None
    except Exception as e:
        logger.error("sync_from_sheets: %s", e)
        return None, None
