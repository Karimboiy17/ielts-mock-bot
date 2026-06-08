from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup


def main_menu_reply():
    """Persistent reply keyboard at bottom of chat."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📋 Mavjud slotlar")],
            [KeyboardButton("📅 Mening bandlovlarim"), KeyboardButton("❌ Bandlovni bekor qilish")],
        ],
        resize_keyboard=True,
    )


def main_menu():
    """Inline keyboard (used for back navigation)."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Mavjud slotlar", callback_data="slots")],
        [InlineKeyboardButton("📅 Mening bandlovlarim", callback_data="mybookings")],
        [InlineKeyboardButton("❌ Bandlovni bekor qilish", callback_data="cancel_menu")],
    ])


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
