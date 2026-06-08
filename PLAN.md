# IELTS Zone Mock Exam Booking Bot — Implementation Plan

> **For Hermes:** Implement this plan task-by-task.

**Goal:** Telegram bot where IELTS Zone students can view available mock exam slots and book them; teachers can manage their availability.

**Architecture:** Python bot using `python-telegram-bot` library, SQLite database, deployed on Railway via GitHub.

**Tech Stack:** Python 3.11, python-telegram-bot, SQLite, Railway, GitHub

---

## Project Structure

```
/home/karimboy/projects/ielts-mock-bot/
├── bot.py              # Main bot entry point
├── db.py               # Database setup + queries
├── handlers/
│   ├── __init__.py
│   ├── student.py      # Student commands (/book, /slots, /mybookings)
│   ├── teacher.py      # Teacher commands (/addslot, /myslots, /removeslot)
│   └── admin.py        # Admin commands (/addteacher, /removeteacher)
├── keyboard.py          # Inline keyboards
├── config.py            # Config loading (env vars)
├── requirements.txt     # Dependencies
├── Procfile             # Railway deployment
├── .env.example         # Template for env vars
└── .gitignore
```

---

## Database Schema (SQLite)

```sql
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name TEXT NOT NULL,
    username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    date TEXT NOT NULL,           -- '2026-06-15'
    time TEXT NOT NULL,           -- '14:00'
    status TEXT DEFAULT 'available',  -- available / booked / cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id INTEGER NOT NULL,
    student_telegram_id INTEGER NOT NULL,
    student_name TEXT NOT NULL,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (slot_id) REFERENCES slots(id)
);
```

---

## Bot Commands

| Command | Who | What |
|---------|-----|------|
| `/start` | Anyone | Welcome + menu |
| `/slots` | Any student | List all available slots (teacher, date, time) |
| `/book` | Any student | Book a slot (picks from available) |
| `/mybookings` | Any student | View their bookings |
| `/cancel` | Any student | Cancel a booking |
| `/addslot 2026-06-15 14:00` | Teacher | Add availability |
| `/myslots` | Teacher | View their slots |
| `/removeslot <id>` | Teacher | Remove a slot |
| `/addteacher @username Name` | Admin | Register teacher |
| `/removeteacher @username` | Admin | Remove teacher |

---

## Tasks

### Task 1: Create project structure and init git

**Files:** All project files

```bash
mkdir -p /home/karimboy/projects/ielts-mock-bot/handlers
cd /home/karimboy/projects/ielts-mock-bot
git init
```

---

### Task 2: Write requirements.txt and Procfile

**Create:** `requirements.txt`
```
python-telegram-bot==21.10
```

**Create:** `Procfile`
```
worker: python bot.py
```

**Create:** `.env.example`
```
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=1054482233
```

---

### Task 3: Write config.py

**Create:** `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment")
```

---

### Task 4: Write db.py (database layer)

**Create:** `db.py`

```python
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
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (slot_id) REFERENCES slots(id)
        );
    """)
    conn.commit()
    conn.close()

# --- Teacher queries ---
def is_teacher(telegram_id):
    conn = get_db()
    row = conn.execute("SELECT id FROM teachers WHERE telegram_id = ?", (telegram_id,)).fetchone()
    conn.close()
    return row is not None

def add_slot(teacher_id, date, time):
    conn = get_db()
    conn.execute("INSERT INTO slots (teacher_id, date, time, status) VALUES (?, ?, ?, 'available')", (teacher_id, date, time))
    conn.commit()
    conn.close()

def get_teacher_slots(teacher_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT s.id, s.date, s.time, s.status, 
               b.student_name, b.student_telegram_id
        FROM slots s
        LEFT JOIN bookings b ON b.slot_id = s.id
        WHERE s.teacher_id = ?
        ORDER BY s.date, s.time
    """, (teacher_id,)).fetchall()
    conn.close()
    return rows

def remove_slot(slot_id, teacher_id):
    conn = get_db()
    conn.execute("DELETE FROM slots WHERE id = ? AND teacher_id = ? AND status = 'available'", (slot_id, teacher_id))
    conn.commit()
    conn.close()

# --- Student queries ---
def get_available_slots():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.id, s.date, s.time, t.name as teacher_name
        FROM slots s
        JOIN teachers t ON t.id = s.teacher_id
        WHERE s.status = 'available'
        ORDER BY s.date, s.time
        LIMIT 20
    """).fetchall()
    conn.close()
    return rows

def book_slot(slot_id, student_telegram_id, student_name):
    conn = get_db()
    # Check if available
    slot = conn.execute("SELECT id FROM slots WHERE id = ? AND status = 'available'", (slot_id,)).fetchone()
    if not slot:
        conn.close()
        return False
    conn.execute("UPDATE slots SET status = 'booked' WHERE id = ?", (slot_id,))
    conn.execute("INSERT INTO bookings (slot_id, student_telegram_id, student_name) VALUES (?, ?, ?)", (slot_id, student_telegram_id, student_name))
    conn.commit()
    conn.close()
    return True

def get_student_bookings(student_telegram_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT b.id, b.slot_id, s.date, s.time, t.name as teacher_name, b.booked_at
        FROM bookings b
        JOIN slots s ON s.id = b.slot_id
        JOIN teachers t ON t.id = s.teacher_id
        WHERE b.student_telegram_id = ?
        ORDER BY s.date, s.time
    """, (student_telegram_id,)).fetchall()
    conn.close()
    return rows

def cancel_booking(booking_id, student_telegram_id):
    conn = get_db()
    booking = conn.execute("SELECT slot_id FROM bookings WHERE id = ? AND student_telegram_id = ?", (booking_id, student_telegram_id)).fetchone()
    if not booking:
        conn.close()
        return False
    conn.execute("UPDATE slots SET status = 'available' WHERE id = ?", (booking["slot_id"],))
    conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return True

# --- Admin queries ---
def add_teacher(telegram_id, name, username):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO teachers (telegram_id, name, username) VALUES (?, ?, ?)", (telegram_id, name, username))
    conn.commit()
    conn.close()

def remove_teacher(telegram_id):
    conn = get_db()
    conn.execute("DELETE FROM teachers WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()
```

---

### Task 5: Write keyboard.py (inline keyboards)

**Create:** `keyboard.py`

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Mavjud slotlar", callback_data="slots")],
        [InlineKeyboardButton("📅 Mening bandlovlarim", callback_data="mybookings")],
        [InlineKeyboardButton("❌ Bandlovni bekor qilish", callback_data="cancel_menu")],
    ])

def slots_keyboard(slots):
    buttons = []
    for s in slots:
        label = f"{s['teacher_name']} | {s['date']} | {s['time']}"
        buttons.append([InlineKeyboardButton(f"📌 {label}", callback_data=f"book_{s['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)

def cancel_keyboard(bookings):
    buttons = []
    for b in bookings:
        label = f"❌ {b['teacher_name']} | {b['date']} | {b['time']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"cancel_{b['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")]])
```

---

### Task 6: Write handlers/student.py

**Create:** `handlers/student.py`

```python
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from db import get_available_slots, book_slot, get_student_bookings, cancel_booking
from keyboard import main_menu, slots_keyboard, cancel_keyboard

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available = get_available_slots()
    if not available:
        await update.message.reply_text("❌ Hozircha band qilish uchun ochiq slot yo'q.")
        return
    await update.message.reply_text("📋 *Mavjud slotlar:*", reply_markup=slots_keyboard(available), parse_mode="Markdown")

async def mybookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookings = get_student_bookings(update.effective_user.id)
    if not bookings:
        await update.message.reply_text("📭 Sizda hozircha bandlov yo'q.")
        return
    msg = "*📅 Sizning bandlovlaringiz:*\n\n"
    for b in bookings:
        msg += f"• {b['teacher_name']} — {b['date']} {b['time']}\n"
    msg += "\n❌ Bekor qilish uchun /cancel"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookings = get_student_bookings(update.effective_user.id)
    if not bookings:
        await update.message.reply_text("📭 Bekor qilish uchun bandlov yo'q.")
        return
    await update.message.reply_text("Qaysi bandlovni bekor qilasiz?", reply_markup=cancel_keyboard(bookings))

# --- Callback handlers ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "slots":
        available = get_available_slots()
        if not available:
            await query.edit_message_text("❌ Hozircha ochiq slot yo'q.", reply_markup=None)
        else:
            await query.edit_message_text("📋 *Mavjud slotlar:*", reply_markup=slots_keyboard(available), parse_mode="Markdown")

    elif data.startswith("book_"):
        slot_id = int(data.split("_")[1])
        user = update.effective_user
        name = user.full_name or user.username or str(user.id)
        success = book_slot(slot_id, user.id, name)
        if success:
            await query.edit_message_text("✅ *Band qilindi!*", parse_mode="Markdown", reply_markup=main_menu())
        else:
            await query.edit_message_text("⚠️ Bu slot allaqachon band qilingan.", reply_markup=main_menu())

    elif data == "mybookings":
        bookings = get_student_bookings(update.effective_user.id)
        if not bookings:
            await query.edit_message_text("📭 Sizda hozircha bandlov yo'q.", reply_markup=main_menu())
        else:
            msg = "*📅 Sizning bandlovlaringiz:*\n\n"
            for b in bookings:
                msg += f"• {b['teacher_name']} — {b['date']} {b['time']}\n"
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=main_menu())

    elif data == "cancel_menu":
        bookings = get_student_bookings(update.effective_user.id)
        if not bookings:
            await query.edit_message_text("📭 Bekor qilish uchun bandlov yo'q.", reply_markup=main_menu())
        else:
            await query.edit_message_text("Qaysi bandlovni bekor qilasiz?", reply_markup=cancel_keyboard(bookings))

    elif data.startswith("cancel_"):
        booking_id = int(data.split("_")[1])
        success = cancel_booking(booking_id, update.effective_user.id)
        if success:
            await query.edit_message_text("✅ Bandlov bekor qilindi.", reply_markup=main_menu())
        else:
            await query.edit_message_text("⚠️ Bekor qilib bo'lmadi.", reply_markup=main_menu())

    elif data == "back_menu":
        await query.edit_message_text("🏠 *Bosh menyu:*", reply_markup=main_menu(), parse_mode="Markdown")
```

---

### Task 7: Write handlers/teacher.py

**Create:** `handlers/teacher.py`

```python
from telegram import Update
from telegram.ext import ContextTypes
from db import is_teacher, add_slot, get_teacher_slots, remove_slot

async def addslot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_teacher(update.effective_user.id):
        await update.message.reply_text("⛔ Siz o'qituvchi emassiz.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("📝 Format: `/addslot YYYY-MM-DD HH:MM`\nMasalan: `/addslot 2026-06-15 14:00`", parse_mode="Markdown")
        return

    date, time = args[0], args[1]
    add_slot(update.effective_user.id, date, time)
    await update.message.reply_text(f"✅ Slot qo'shildi: {date} {time}")

async def myslots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_teacher(update.effective_user.id):
        await update.message.reply_text("⛔ Siz o'qituvchi emassiz.")
        return

    slots = get_teacher_slots(update.effective_user.id)
    if not slots:
        await update.message.reply_text("📭 Sizda hozircha slot yo'q.")
        return

    msg = "*📅 Sizning slotlaringiz:*\n\n"
    for s in slots:
        status_icon = "🔴" if s["status"] == "booked" else "🟢"
        student = f" — {s['student_name']}" if s['student_name'] else ""
        msg += f"{status_icon} `{s['date']}` `{s['time']}`{student} (ID: {s['id']})\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def removeslot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_teacher(update.effective_user.id):
        await update.message.reply_text("⛔ Siz o'qituvchi emassiz.")
        return

    if not context.args:
        await update.message.reply_text("📝 Format: `/removeslot <slot_id>`\nSlot ID larni ko'rish uchun /myslots")
        return

    slot_id = int(context.args[0])
    remove_slot(slot_id, update.effective_user.id)
    await update.message.reply_text(f"✅ Slot #{slot_id} o'chirildi.")
```

---

### Task 8: Write handlers/admin.py

**Create:** `handlers/admin.py`

```python
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from db import add_teacher, remove_teacher

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def addteacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Faqat admin uchun.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("📝 O'qituvchining xabariga reply qilib `/addteacher Ismi` yozing.")
        return

    target_user = update.message.reply_to_message.from_user
    name = " ".join(context.args) if context.args else target_user.full_name
    username = f"@{target_user.username}" if target_user.username else ""

    add_teacher(target_user.id, name, username)
    await update.message.reply_text(f"✅ O'qituvchi qo'shildi: {name} ({username})")

async def removeteacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Faqat admin uchun.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("📝 O'qituvchining xabariga reply qilib `/removeteacher` yozing.")
        return

    target_user = update.message.reply_to_message.from_user
    remove_teacher(target_user.id)
    await update.message.reply_text(f"✅ O'qituvchi o'chirildi: {target_user.full_name}")
```

---

### Task 9: Write bot.py (main entry point)

**Create:** `bot.py`

```python
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from db import init_db
from handlers.student import slots, mybookings, cancel_cmd, button_handler
from handlers.teacher import addslot, myslots, removeslot
from handlers.admin import addteacher, removeteacher

async def start(update, context):
    msg = (
        "🏫 *IELTS Zone — Mock Exam Booking*\n\n"
        "Mock imtihonlarni band qilish botiga xush kelibsiz!\n\n"
        "📋 /slots — Mavjud vaqtlarni ko'rish\n"
        "📅 /mybookings — Mening bandlovlarim\n"
        "❌ /cancel — Bandlovni bekor qilish\n\n"
        "🧑‍🏫 *O'qituvchilar uchun:*\n"
        "➕ /addslot <sana> <vaqt> — Slot qo'shish\n"
        "📋 /myslots — Slotlarimni ko'rish\n"
        "🗑 /removeslot <id> — Slot o'chirish"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Student commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("slots", slots))
    app.add_handler(CommandHandler("mybookings", mybookings))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    # Teacher commands
    app.add_handler(CommandHandler("addslot", addslot))
    app.add_handler(CommandHandler("myslots", myslots))
    app.add_handler(CommandHandler("removeslot", removeslot))

    # Admin commands
    app.add_handler(CommandHandler("addteacher", addteacher))
    app.add_handler(CommandHandler("removeteacher", removeteacher))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 Mock Booking Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
```

---

### Task 10: Write .gitignore

**Create:** `.gitignore`

```
__pycache__/
*.pyc
.env
bookings.db
venv/
.venv/
*.egg-info/
```

---

### Task 11: First commit + Push to GitHub

```bash
cd /home/karimboy/projects/ielts-mock-bot
git add -A
git commit -m "feat: IELTS Zone mock exam booking Telegram bot"
```

Then:
1. Create repo on GitHub (`ielts-mock-bot`)
2. Add remote and push:
```bash
git remote add origin https://github.com/KarimboyX/ielts-mock-bot.git
git branch -M main
git push -u origin main
```

---

### Task 12: Create Telegram bot via BotFather

1. Open Telegram → @BotFather
2. `/newbot` → name: "IELTS Zone Mock Booking"
3. username: `ielts_mock_bot` (or similar)
4. Copy the token
5. Get the bot token → set in Railway env var `BOT_TOKEN`

---

### Task 13: Deploy to Railway

1. Go to https://railway.app
2. New → Deploy from GitHub repo → select `ielts-mock-bot`
3. Set env vars: `BOT_TOKEN=...`, `ADMIN_IDS=1054482233`
4. Deploy!

---

## Verification

1. Student opens bot → `/start` → sees welcome + menu
2. Teacher adds slot: `/addslot 2026-06-15 14:00` → gets confirmation
3. Student runs `/slots` → sees available slots
4. Student clicks slot → gets booking confirmation
5. Student runs `/mybookings` → sees booking
6. Teacher runs `/myslots` → sees booked status
7. Student cancels booking → slot becomes available again

---

## Risks & Notes

- Railway may require payment method after free trial
- Bot token must be secure — never commit to git
- Teacher registration is manual (admin adds) — good for small teams
- No role verification for students — any Telegram user can book
- SQLite works on Railway single instance, not multi-replica
