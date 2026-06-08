"""Student handlers — trilingual, with payment flow."""
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from db import (
    get_available_slots, request_booking, get_student_bookings,
    cancel_booking, get_language,
)
from i18n import t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handled in bot.py — this is a fallback."""
    from keyboard import lang_picker_keyboard
    await update.message.reply_text(
        "🇺🇿 Tilni tanlang / 🇬🇧 Choose language / 🇷🇺 Выберите язык",
        reply_markup=lang_picker_keyboard(),
    )


async def slots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)
    slots = get_available_slots()
    if not slots:
        await update.message.reply_text(t("no_slots", lang))
        return

    text = t("click_to_book", lang) + "\n\n"
    buttons = []
    for s in slots:
        label = f"{s['date']} {s['time']} — {s['teacher_name']}"
        cb = f"book_{s['id']}"
        buttons.append([InlineKeyboardButton(label, callback_data=cb)])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def mybookings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)
    bookings = get_student_bookings(uid)
    if not bookings:
        await update.message.reply_text(t("no_bookings", lang))
        return

    text = t("your_bookings", lang)
    status_icons = {
        "pending": {"uz": "⏳ Kutilmoqda", "en": "⏳ Pending", "ru": "⏳ Ожидает"},
        "accepted": {"uz": "✅ Tasdiqlangan", "en": "✅ Confirmed", "ru": "✅ Подтверждено"},
        "rejected": {"uz": "❌ Rad etilgan", "en": "❌ Rejected", "ru": "❌ Отклонено"},
    }
    for b in bookings:
        icon = status_icons.get(b["status"], {"uz": "❓", "en": "❓", "ru": "❓"})
        st = icon.get(lang, icon["uz"])
        text += f"{st} — {b['date']} {b['time']} ({b['teacher_name']})\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)
    bookings = get_student_bookings(uid)
    if not bookings:
        await update.message.reply_text(t("no_bookings_to_cancel", lang))
        return

    text = t("cancel_prompt", lang) + "\n\n"
    buttons = []
    for b in bookings:
        label = f"/cancel_{b['id']} — {b['date']} {b['time']} ({b['teacher_name']})"
        cb = f"cancel_{b['id']}"
        buttons.append([InlineKeyboardButton(label, callback_data=cb)])

    text += t("cancel_usage", lang)
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle student inline button callbacks."""
    query = update.callback_query
    data = query.data
    uid = update.effective_user.id
    lang = get_language(uid)

    # Book a slot
    if data.startswith("book_"):
        slot_id = int(data.replace("book_", ""))
        student_name = update.effective_user.full_name or "Student"
        student_username = update.effective_user.username or ""

        result = request_booking(slot_id, uid, student_name, student_username)
        if not result:
            await query.answer("⚠️ Bu slot allaqachon band!", show_alert=True)
            await query.edit_message_reply_markup(reply_markup=None)
            return

        # Get slot info for the message
        from db import get_db
        conn = get_db()
        slot = conn.execute(
            "SELECT s.date, s.time, t.name as teacher_name FROM slots s "
            "JOIN teachers t ON t.id = s.teacher_id WHERE s.id = ?",
            (slot_id,),
        ).fetchone()
        conn.close()

        if slot:
            text = t("payment_required", lang,
                     date=slot["date"], time=slot["time"], teacher=slot["teacher_name"])
        else:
            text = t("payment_received", lang)

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
        )
        await query.answer()

    # Cancel a booking
    elif data.startswith("cancel_"):
        booking_id = int(data.replace("cancel_", ""))
        if cancel_booking(booking_id, uid):
            await query.edit_message_text(
                t("booking_cancelled", lang),
                parse_mode="Markdown",
            )
        else:
            await query.answer("⚠️ Bekor qilib bo'lmadi!", show_alert=True)
        await query.answer()

    else:
        await query.answer()
