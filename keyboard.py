from datetime import date, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup


def main_menu_reply(is_admin=False):
    """Persistent reply keyboard at bottom of chat."""
    if is_admin:
        # Admin sees ONLY admin panel
        rows = [
            [KeyboardButton("➕ Yangi slot"), KeyboardButton("📊 Slotlarim")],
            [KeyboardButton("🔄 Doimiy slot qo'shish"), KeyboardButton("📋 Doimiy slotlarim")],
            [KeyboardButton("👨‍🏫 O'qituvchi qo'shish"), KeyboardButton("👥 O'qituvchilar")],
            [KeyboardButton("📊 Barcha bandlovlar")],
        ]
    else:
        # Students see only student options
        rows = [
            [KeyboardButton("📋 Mavjud slotlar")],
            [KeyboardButton("📅 Mening bandlovlarim"), KeyboardButton("❌ Bandlovni bekor qilish")],
        ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def main_menu(is_admin=False):
    """Inline keyboard (used for back navigation)."""
    buttons = [
        [InlineKeyboardButton("📋 Mavjud slotlar", callback_data="slots")],
        [InlineKeyboardButton("📅 Mening bandlovlarim", callback_data="mybookings")],
        [InlineKeyboardButton("❌ Bandlovni bekor qilish", callback_data="cancel_menu")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def date_picker_keyboard():
    """Show next 7 days for slot date selection."""
    today = date.today()
    buttons = []
    for i in range(7):
        d = today + timedelta(days=i)
        label = f"📅 {d.strftime('%d %b (%a)')}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"addslot_date_{d.isoformat()}")])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def time_picker_keyboard(selected_date):
    """Show time slots for a selected date."""
    times = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    buttons = []
    row = []
    for t in times:
        row.append(InlineKeyboardButton(t, callback_data=f"addslot_time_{selected_date}_{t}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Boshqa sana", callback_data="addslot_pick_date")])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)



def slots_keyboard(slots):
    buttons = []
    for s in slots:
        label = f"{s['teacher_name']} | {s['date']} | {s['time']}"
        buttons.append([
            InlineKeyboardButton(f"📌 {label}", callback_data=f"book_{s['id']}")
        ])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def cancel_keyboard(bookings):
    buttons = []
    for b in bookings:
        label = f"❌ {b['teacher_name']} | {b['date']} | {b['time']}"
        buttons.append([
            InlineKeyboardButton(label, callback_data=f"cancel_{b['id']}")
        ])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def teacher_confirm_keyboard(booking_id, student_name):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"accept_{booking_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{booking_id}"),
        ]
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")]
    ])


# ── Recurring Patterns ────────────────────────────────────

def day_picker_keyboard():
    """Pick a day of the week for recurring slots."""
    days = [
        ("Dushanba", 0), ("Seshanba", 1), ("Chorshanba", 2),
        ("Payshanba", 3), ("Juma", 4), ("Shanba", 5), ("Yakshanba", 6),
    ]
    buttons = []
    row = []
    for name, dow in days:
        row.append(InlineKeyboardButton(name, callback_data=f"recur_day_{dow}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def time_picker_recurring_keyboard(day_of_week):
    """Pick a time for a recurring pattern."""
    times = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    buttons = []
    row = []
    for t in times:
        row.append(InlineKeyboardButton(t, callback_data=f"recur_time_{day_of_week}_{t}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Boshqa kun", callback_data="recur_pick_day")])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)


def recurring_list_keyboard(patterns):
    """Show recurring patterns with delete option."""
    from db import DAY_NAMES
    buttons = []
    for p in patterns:
        day_name = DAY_NAMES.get(p["day_of_week"], str(p["day_of_week"]))
        label = f"🗑 {day_name} {p['time']}"
        buttons.append([
            InlineKeyboardButton(label, callback_data=f"recur_del_{p['id']}")
        ])
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(buttons)
