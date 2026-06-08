from telegram import Update
from telegram.ext import ContextTypes

from db import (
    get_available_slots, request_booking, get_student_bookings,
    cancel_booking, get_teacher_by_id, confirm_booking, reject_booking,
)
from keyboard import main_menu, main_menu_reply, slots_keyboard, cancel_keyboard, teacher_confirm_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 *IELTS Zone Mock Booking*\n\n"
        "Mock imtihon uchun o'qituvchi band qilish boti.\n\n"
        "Quyidagi menyudan tanlang:",
        reply_markup=main_menu_reply(),
        parse_mode="Markdown",
    )


async def slots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows available slots with inline buttons for booking."""
    available = get_available_slots()
    if not available:
        await update.message.reply_text(
            "❌ Hozircha band qilish uchun ochiq slot yo'q.",
            reply_markup=main_menu_reply(),
        )
        return
    await update.message.reply_text(
        "📋 *Mavjud slotlar:*\n\nBirini tanlang — so'rov o'qituvchiga boradi.",
        reply_markup=slots_keyboard(available),
        parse_mode="Markdown",
    )


async def mybookings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookings = get_student_bookings(update.effective_user.id)
    if not bookings:
        await update.message.reply_text(
            "📭 Sizda hozircha bandlov yo'q.",
            reply_markup=main_menu_reply(),
        )
        return
    msg = "*📅 Sizning bandlovlaringiz:*\n\n"
    status_map = {
        "pending": "⏳",
        "accepted": "✅",
        "rejected": "❌",
    }
    for b in bookings:
        icon = status_map.get(b["status"], "❓")
        msg += f"{icon} {b['teacher_name']} — {b['date']} {b['time']}\n"
    msg += "\n❌ Bekor qilish uchun /cancel"
    await update.message.reply_text(
        msg,
        reply_markup=main_menu_reply(),
        parse_mode="Markdown",
    )


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookings = get_student_bookings(update.effective_user.id)
    if not bookings:
        await update.message.reply_text(
            "📭 Bekor qilish uchun bandlov yo'q.",
            reply_markup=main_menu_reply(),
        )
        return
    await update.message.reply_text(
        "Qaysi bandlovni bekor qilasiz?",
        reply_markup=cancel_keyboard(bookings),
    )


# ─── Single callback handler for ALL inline buttons ─────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if data == "slots":
        available = get_available_slots()
        if not available:
            await query.edit_message_text(
                "❌ Hozircha ochiq slot yo'q.",
                reply_markup=main_menu(),
            )
        else:
            await query.edit_message_text(
                "📋 *Mavjud slotlar:*\n\nBirini tanlang — so'rov o'qituvchiga boradi.",
                reply_markup=slots_keyboard(available),
                parse_mode="Markdown",
            )

    elif data.startswith("book_"):
        slot_id = int(data.split("_")[1])
        name = user.full_name or user.username or str(user.id)
        username = f"@{user.username}" if user.username else ""

        result = request_booking(slot_id, user.id, name, username)
        if result is None:
            await query.edit_message_text(
                "⚠️ Bu slot allaqachon band qilingan yoki mavjud emas.",
                reply_markup=main_menu(),
            )
            return

        # Notify teacher
        teacher = get_teacher_by_id(result["teacher_db_id"])
        if teacher:
            msg = (
                f"📩 *Yangi mock so'rovi!*\n\n"
                f"👤 O'quvchi: {name}"
            )
            if username:
                msg += f" ({username})"
            msg += f"\n🆔 Booking ID: `{result['booking_id']}`"
            try:
                await context.bot.send_message(
                    chat_id=teacher["telegram_id"],
                    text=msg,
                    reply_markup=teacher_confirm_keyboard(result["booking_id"], name),
                    parse_mode="Markdown",
                )
            except Exception:
                pass  # teacher may have blocked bot; admin can follow up

        await query.edit_message_text(
            "⏳ *So'rov yuborildi!*\n\n"
            "O'qituvchi tasdiqlagandan keyin sizga xabar keladi.",
            reply_markup=main_menu(),
            parse_mode="Markdown",
        )

    elif data == "mybookings":
        bookings = get_student_bookings(user.id)
        if not bookings:
            await query.edit_message_text(
                "📭 Sizda hozircha bandlov yo'q.",
                reply_markup=main_menu(),
            )
        else:
            msg = "*📅 Sizning bandlovlaringiz:*\n\n"
            status_map = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}
            for b in bookings:
                icon = status_map.get(b["status"], "❓")
                msg += f"{icon} {b['teacher_name']} — {b['date']} {b['time']}\n"
            await query.edit_message_text(
                msg,
                reply_markup=main_menu(),
                parse_mode="Markdown",
            )

    elif data == "cancel_menu":
        bookings = get_student_bookings(user.id)
        if not bookings:
            await query.edit_message_text(
                "📭 Bekor qilish uchun bandlov yo'q.",
                reply_markup=main_menu(),
            )
        else:
            await query.edit_message_text(
                "Qaysi bandlovni bekor qilasiz?",
                reply_markup=cancel_keyboard(bookings),
            )

    elif data.startswith("cancel_"):
        booking_id = int(data.split("_")[1])
        success = cancel_booking(booking_id, user.id)
        if success:
            await query.edit_message_text(
                "✅ Bandlov bekor qilindi.",
                reply_markup=main_menu(),
            )
        else:
            await query.edit_message_text(
                "⚠️ Bekor qilib bo'lmadi.",
                reply_markup=main_menu(),
            )

    elif data.startswith("accept_"):
        booking_id = int(data.split("_")[1])
        result = confirm_booking(booking_id, user.id)
        if result is None:
            await query.edit_message_text(
                "⚠️ Bu so'rov allaqachon ko'rib chiqilgan yoki sizga tegishli emas.",
            )
            return
        try:
            await context.bot.send_message(
                chat_id=result["student_telegram_id"],
                text="✅ *Bandlovingiz tasdiqlandi!*\n\nO'qituvchi so'rovingizni qabul qildi.",
                parse_mode="Markdown",
            )
        except Exception:
            pass
        await query.edit_message_text(
            f"✅ {result['student_name']} uchun bandlov tasdiqlandi.",
        )

    elif data.startswith("reject_"):
        booking_id = int(data.split("_")[1])
        result = reject_booking(booking_id, user.id)
        if result is None:
            await query.edit_message_text(
                "⚠️ Bu so'rov allaqachon ko'rib chiqilgan yoki sizga tegishli emas.",
            )
            return
        try:
            await context.bot.send_message(
                chat_id=result["student_telegram_id"],
                text="❌ *Bandlovingiz rad etildi.*\n\nO'qituvchi so'rovingizni qabul qilmadi. Qaytadan urinib ko'ring.",
                parse_mode="Markdown",
            )
        except Exception:
            pass
        await query.edit_message_text(
            f"❌ {result['student_name']} uchun bandlov rad etildi.",
        )

    elif data == "back_menu":
        await query.edit_message_text(
            "🏠 *Bosh menyu:*",
            reply_markup=main_menu(),
            parse_mode="Markdown",
        )
