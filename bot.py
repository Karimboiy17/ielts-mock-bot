from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN, ADMIN_IDS, TEACHER_IDS
from db import init_db, is_teacher, add_teacher, add_slot, get_all_bookings, get_all_teachers
from handlers.student import (
    start, slots_cmd, mybookings_cmd, cancel_cmd, button_handler,
)
from handlers.teacher import addslot_cmd, myslots_cmd, removeslot_cmd
from handlers.admin import addteacher_cmd, removeteacher_cmd
from keyboard import (
    date_picker_keyboard, time_picker_keyboard,
    day_picker_keyboard, time_picker_recurring_keyboard, recurring_list_keyboard,
)


def is_admin(user_id):
    return user_id in ADMIN_IDS


def is_teacher_or_env(user_id):
    """Check if user is a teacher (by DB or env var)."""
    return user_id in TEACHER_IDS or is_teacher(user_id)


def _auto_register_teacher(uid, name="Teacher"):
    """Register user as teacher if in TEACHER_IDS but not yet in DB."""
    if uid in TEACHER_IDS and not is_teacher(uid):
        add_teacher(uid, name)


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
    elif text in ("➕ Yangi slot", "🔄 Doimiy slot qo'shish", "📋 Doimiy slotlarim", "📊 Slotlarim"):
        if not is_admin(uid) and not is_teacher_or_env(uid):
            await update.message.reply_text("⛔ Admin huquqi kerak.")
            return
        if not is_teacher(uid):
            _auto_register_teacher(uid, update.effective_user.full_name or "Teacher")

        if text == "➕ Yangi slot":
            await update.message.reply_text(
                "📅 *Slot sanasini tanlang:*",
                reply_markup=date_picker_keyboard(),
                parse_mode="Markdown",
            )
        elif text == "🔄 Doimiy slot qo'shish":
            await update.message.reply_text(
                "📅 *Doimiy slot uchun kunni tanlang:* (har hafta shu kuni slot ochiladi)",
                reply_markup=day_picker_keyboard(),
                parse_mode="Markdown",
            )
        elif text == "📋 Doimiy slotlarim":
            from db import get_recurring_patterns, DAY_NAMES
            patterns = get_recurring_patterns(uid)
            if not patterns:
                await update.message.reply_text("📭 Hozircha doimiy slotlar yo'q.\n\n🔄 *Doimiy slot qo'shish* tugmasini bosing.",
                                               parse_mode="Markdown")
                return
            msg = "*📋 Doimiy slotlaringiz:*\n\n"
            for p in patterns:
                day_name = DAY_NAMES.get(p["day_of_week"], str(p["day_of_week"]))
                msg += f"• {day_name} — {p['time']}\n"
            msg += "\n🗑 O'chirish uchun pastdagi slotni bosing:"
            await update.message.reply_text(
                msg,
                reply_markup=recurring_list_keyboard(patterns),
                parse_mode="Markdown",
            )
        elif text == "📊 Slotlarim":
            await myslots_cmd(update, context)
    elif text == "👨‍🏫 O'qituvchi qo'shish":
        await update.message.reply_text(
            "📝 *O'qituvchi qo'shish* — quyidagi usullardan birini ishlating:\n\n"
            "1️⃣ O'qituvchining biror xabariga *reply* qilib `/addteacher Ismi` yozing\n"
            "2️⃣ `/addteacher @username Ismi` yozing\n"
            "3️⃣ `/addteacher <Telegram_ID> Ismi` yozing\n\n"
            "👤 Agar o'qituvchi botga hech qachon xabar yozmagan bo'lsa, "
            "avval unga `@ieltszonemockbot` ga `/start` yozishini so'rang.",
            parse_mode="Markdown",
        )
    elif text == "📊 Barcha bandlovlar":
        if not is_admin(uid):
            await update.message.reply_text("⛔ Admin huquqi kerak.")
            return
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
    elif text == "👥 O'qituvchilar":
        if not is_admin(uid):
            await update.message.reply_text("⛔ Admin huquqi kerak.")
            return
        teachers = get_all_teachers()
        if not teachers:
            await update.message.reply_text("📭 Hozircha o'qituvchilar yo'q.")
            return
        msg = "*👥 Ro'yxatdagi o'qituvchilar:*\n\n"
        for t in teachers:
            uname = f" (@{t['username']})" if t.get('username') else ""
            msg += f"• {t['name']}{uname} — ID: `{t['telegram_id']}`\n"
        await update.message.reply_text(msg, parse_mode="Markdown")


# ── Unified callback handler ──

_original_button_handler = button_handler


async def unified_button_handler(update: Update, context):
    """Handles ALL inline button callbacks."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    uid = user.id

    # ── Add-slot flow ──
    if data.startswith("addslot_"):
        if not is_admin(uid) and not is_teacher_or_env(uid):
            await query.answer("⛔ Admin huquqi kerak.", show_alert=True)
            return

        if not is_teacher(uid):
            _auto_register_teacher(uid, user.full_name or "Teacher")

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
            parts = data.replace("addslot_time_", "", 1)
            idx = parts.rfind("_")
            selected_date = parts[:idx]
            selected_time = parts[idx + 1:]
            add_slot(uid, selected_date, selected_time)
            text = (
                f"✅ *Slot qo'shildi!*\n\n"
                f"📅 Sana: {selected_date}\n"
                f"🕐 Vaqt: {selected_time}"
            )
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=date_picker_keyboard(),
                    parse_mode="Markdown",
                )
            except Exception:
                await update.effective_message.reply_text(text, parse_mode="Markdown")
        await query.answer()
        return

    # ── Recurring pattern flow ──
    if data.startswith("recur_"):
        if not is_admin(uid) and not is_teacher_or_env(uid):
            await query.answer("⛔ Admin huquqi kerak.", show_alert=True)
            return

        if not is_teacher(uid):
            _auto_register_teacher(uid, user.full_name or "Teacher")

        if data == "recur_pick_day":
            await query.edit_message_text(
                "📅 *Doimiy slot uchun kunni tanlang:*",
                reply_markup=day_picker_keyboard(),
                parse_mode="Markdown",
            )
        elif data.startswith("recur_day_"):
            day_of_week = int(data.replace("recur_day_", ""))
            from db import DAY_NAMES
            day_name = DAY_NAMES.get(day_of_week, str(day_of_week))
            await query.edit_message_text(
                f"🕐 *{day_name} — vaqtni tanlang:*",
                reply_markup=time_picker_recurring_keyboard(day_of_week),
                parse_mode="Markdown",
            )
        elif data.startswith("recur_time_"):
            # recur_time_3_14:00
            parts = data.replace("recur_time_", "", 1)
            idx = parts.find("_")
            day_of_week = int(parts[:idx])
            selected_time = parts[idx + 1:]
            from db import add_recurring_pattern, generate_slots_from_patterns, DAY_NAMES
            day_name = DAY_NAMES.get(day_of_week, str(day_of_week))
            add_recurring_pattern(uid, day_of_week, selected_time)
            count = generate_slots_from_patterns(uid, weeks=4)
            text = (
                f"✅ *Doimiy slot qo'shildi!*\n\n"
                f"📅 Har hafta: *{day_name}*\n"
                f"🕐 Vaqt: {selected_time}\n"
                f"📊 {count} ta yangi slot yaratildi (4 haftaga)"
            )
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=day_picker_keyboard(),
            )
        elif data.startswith("recur_del_"):
            pattern_id = int(data.replace("recur_del_", ""))
            from db import remove_recurring_pattern, get_recurring_patterns, DAY_NAMES
            remove_recurring_pattern(pattern_id, uid)
            patterns = get_recurring_patterns(uid)
            if not patterns:
                await query.edit_message_text(
                    "🗑 *Doimiy slot o'chirildi!* Endi doimiy slotlar yo'q.",
                    parse_mode="Markdown",
                )
            else:
                msg = "*📋 Doimiy slotlaringiz:*\n\n"
                for p in patterns:
                    day_name = DAY_NAMES.get(p["day_of_week"], str(p["day_of_week"]))
                    msg += f"• {day_name} — {p['time']}\n"
                msg += "\n🗑 O'chirish uchun pastdagi slotni bosing:"
                await query.edit_message_text(
                    msg,
                    reply_markup=recurring_list_keyboard(patterns),
                    parse_mode="Markdown",
                )
        await query.answer()
        return

    # ── Fall through to student button handler ──
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

    # Inline button handler
    app.add_handler(CallbackQueryHandler(unified_button_handler))

    # ReplyKeyboard menu handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND &
        (filters.Text("📋 Mavjud slotlar") |
         filters.Text("📅 Mening bandlovlarim") |
         filters.Text("❌ Bandlovni bekor qilish") |
         filters.Text("➕ Yangi slot") |
         filters.Text("🔄 Doimiy slot qo'shish") |
         filters.Text("📋 Doimiy slotlarim") |
         filters.Text("📊 Slotlarim") |
         filters.Text("👨‍🏫 O'qituvchi qo'shish") |
         filters.Text("📊 Barcha bandlovlar") |
         filters.Text("👥 O'qituvchilar")),
        handle_menu_text,
    ))

    import time
    from telegram.error import Conflict

    print("✅ IELTS Mock Booking Bot ishga tushdi!")

    retries = 0
    while True:
        try:
            app.run_polling()
        except Conflict:
            retries += 1
            wait = min(5 * retries, 30)
            print(f"⚠️ Conflict — {wait}s kutib qayta urinish (#{retries})...")
            time.sleep(wait)
        except (KeyboardInterrupt, SystemExit):
            print("🛑 Bot to'xtatildi.")
            break
        except Exception as e:
            print(f"❌ Xato: {e}")
            break


if __name__ == "__main__":
    main()
