from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN, ADMIN_IDS
from db import init_db, is_teacher, add_teacher, add_slot
from handlers.student import (
    start, slots_cmd, mybookings_cmd, cancel_cmd, button_handler,
)
from handlers.teacher import addslot_cmd, myslots_cmd, removeslot_cmd
from handlers.admin import addteacher_cmd, removeteacher_cmd
from keyboard import date_picker_keyboard, time_picker_keyboard, main_menu_reply


def is_admin(user_id):
    return user_id in ADMIN_IDS


async def handle_menu_text(update: Update, context):
    """Handle ReplyKeyboard menu button presses."""
    text = update.message.text
    uid = update.effective_user.id

    if text == "📋 Mavjud slotlar":
        await slots_cmd(update, context)
    elif text == "📅 Mening bandlovlarim":
        await mybookings_cmd(update, context)
    elif text == "❌ Bandlovni bekor qilish":
        await cancel_cmd(update, context)
    elif text == "➕ Yangi slot":
        # Admin: show date picker
        if not is_admin(uid) and not is_teacher(uid):
            await update.message.reply_text("⛔ Admin huquqi kerak.")
            return
        # Auto-register
        if is_admin(uid) and not is_teacher(uid):
            name = update.effective_user.full_name or "Admin"
            add_teacher(uid, name)
        await update.message.reply_text(
            "📅 *Slot sanasini tanlang:*",
            reply_markup=date_picker_keyboard(),
            parse_mode="Markdown",
        )
    elif text == "📊 Slotlarim":
        await myslots_cmd(update, context)
    elif text == "👨‍🏫 O'qituvchi qo'shish":
        await addteacher_cmd(update, context)
    elif text == "📊 Barcha bandlovlar":
        # Admin: show all bookings
        if not is_admin(uid):
            await update.message.reply_text("⛔ Admin huquqi kerak.")
            return
        from db import get_all_bookings
        bookings = get_all_bookings()
        if not bookings:
            await update.message.reply_text("📭 Hozircha hech qanday bandlov yo'q.")
            return
        msg = "*📊 Barcha bandlovlar:*\n\n"
        status_map = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}
        for b in bookings:
            icon = status_map.get(b["status"], "❓")
            msg += f"{icon} {b['student_name']} → {b['teacher_name']} | {b['date']} {b['time']}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")


# ── Also wire add-slot callbacks into the student button_handler ──
# We monkey-patch by extending button_handler in bot.py so we keep one CallbackQueryHandler.

_original_button_handler = button_handler


async def unified_button_handler(update: Update, context):
    """Handles ALL inline button callbacks — student + admin add-slot flow."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    uid = user.id

    # ── Add-slot flow (admin / teacher) ──
    if data.startswith("addslot_"):
        if not is_admin(uid) and not is_teacher(uid):
            await query.answer("⛔ Admin huquqi kerak.", show_alert=True)
            return

        # Auto-register
        if is_admin(uid) and not is_teacher(uid):
            name = user.full_name or "Admin"
            add_teacher(uid, name)

        if data == "addslot_pick_date":
            await query.edit_message_text(
                "📅 *Slot sanasini tanlang:*",
                reply_markup=date_picker_keyboard(),
                parse_mode="Markdown",
            )
        elif data.startswith("addslot_date_"):
            selected_date = data.replace("addslot_date_", "")
            await query.edit_message_text(
                f"🕐 *{selected_date} — vaqtni tanlang:*",
                reply_markup=time_picker_keyboard(selected_date),
                parse_mode="Markdown",
            )
        elif data.startswith("addslot_time_"):
            # addslot_time_2026-06-09_14:00
            parts = data.replace("addslot_time_", "", 1)
            # split on last underscore? No — format is date_time
            # Find last underscore position for time
            idx = parts.rfind("_")
            selected_date = parts[:idx]
            selected_time = parts[idx + 1:]
            add_slot(uid, selected_date, selected_time)
            text = (
                f"✅ *Slot qo'shildi!*\n\n"
                f"📅 Sana: {selected_date}\n"
                f"🕐 Vaqt: {selected_time}"
            )
            # If called from message, need to send new; from callback we can edit
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=date_picker_keyboard(),
                    parse_mode="Markdown",
                )
            except Exception:
                await update.effective_message.reply_text(
                    text,
                    parse_mode="Markdown",
                )
        await query.answer()
        return

    # ── Fall through to original student button handler ──
    await _original_button_handler(update, context)


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # Student commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("slots", slots_cmd))
    app.add_handler(CommandHandler("mybookings", mybookings_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    # Teacher commands
    app.add_handler(CommandHandler("addslot", addslot_cmd))
    app.add_handler(CommandHandler("myslots", myslots_cmd))
    app.add_handler(CommandHandler("removeslot", removeslot_cmd))

    # Admin commands
    app.add_handler(CommandHandler("addteacher", addteacher_cmd))
    app.add_handler(CommandHandler("removeteacher", removeteacher_cmd))

    # Inline button handler (covers all callbacks: student booking + admin add-slot)
    app.add_handler(CallbackQueryHandler(unified_button_handler))

    # ReplyKeyboard menu button handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND &
        (filters.Text("📋 Mavjud slotlar") |
         filters.Text("📅 Mening bandlovlarim") |
         filters.Text("❌ Bandlovni bekor qilish") |
         filters.Text("➕ Yangi slot") |
         filters.Text("📊 Slotlarim") |
         filters.Text("👨‍🏫 O'qituvchi qo'shish") |
         filters.Text("📊 Barcha bandlovlar")),
        handle_menu_text,
    ))

    print("✅ IELTS Mock Booking Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
