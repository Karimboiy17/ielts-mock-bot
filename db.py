import sqlite3

DB = "bookings.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
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
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (slot_id) REFERENCES slots(id)
        );
    """)
    conn.commit()
    conn.close()


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
    conn.execute(
        "INSERT INTO slots (teacher_id, date, time, status) "
        "VALUES ((SELECT id FROM teachers WHERE telegram_id=?), ?, ?, 'available')",
        (teacher_telegram_id, date, time),
    )
    conn.commit()
    conn.close()


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
        LIMIT 20
        """
    ).fetchall()
    conn.close()
    return rows


def request_booking(slot_id, student_telegram_id, student_name, student_username=""):
    """Student requests a booking → slot becomes 'pending'."""
    conn = get_db()
    slot = conn.execute(
        "SELECT id, teacher_id FROM slots WHERE id = ? AND status = 'available'",
        (slot_id,),
    ).fetchone()
    if not slot:
        conn.close()
        return None  # already taken

    conn.execute("UPDATE slots SET status = 'pending' WHERE id = ?", (slot_id,))
    cur = conn.execute(
        "INSERT INTO bookings (slot_id, student_telegram_id, student_name, student_username, status) "
        "VALUES (?, ?, ?, ?, 'pending')",
        (slot_id, student_telegram_id, student_name, student_username),
    )
    booking_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"booking_id": booking_id, "teacher_db_id": slot["teacher_id"]}


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
    # verify teacher owns this slot
    teacher = conn.execute(
        "SELECT id FROM teachers WHERE telegram_id=?", (teacher_telegram_id,)
    ).fetchone()
    if not teacher or teacher["id"] != booking["teacher_id"]:
        conn.close()
        return None

    conn.execute("UPDATE slots SET status = 'booked' WHERE id = ?", (booking["slot_id"],))
    conn.execute("UPDATE bookings SET status = 'accepted' WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
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


def remove_teacher_db(telegram_id):
    conn = get_db()
    conn.execute("DELETE FROM teachers WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()



def get_all_bookings():
    conn = get_db()
    rows = conn.execute(
        "SELECT b.id, b.student_name, b.status, "
        "s.date, s.time, t.name AS teacher_name "
        "FROM bookings b "
        "JOIN slots s ON b.slot_id = s.id "
        "JOIN teachers t ON s.teacher_id = t.id "
        "ORDER BY s.date, s.time"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
