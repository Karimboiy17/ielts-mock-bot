"""IELTS Zone Mock Booking Bot — trilingual, payment receipts, Google Sheets sync."""
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)
from telegram.error import Conflict

from config import BOT_TOKEN, ADMIN_IDS, TEACHER_IDS, GROUP_CHECK_ID
from db import (
    init_db, is_teacher, add_teacher, add_slot, get_all_bookings,
    get_all_teachers, get_language, set_language,
    sync_from_sheets, get_current_payment_for_user,
    submit_payment_receipt, approve_payment, reject_payment,
    get_pending_payments, save_check_forward, find_checks_by_query,
)
from handlers.student import start, slots_cmd, mybookings_cmd, cancel_cmd, button_handler
from handlers.teacher import addslot_cmd, myslots_cmd, removeslot_cmd
from handlers.admin import addteacher_cmd, removeteacher_cmd
from keyboard import (
    lang_picker_keyboard, student_reply_keyboard,
    admin_reply_keyboard, teacher_reply_keyboard,
    date_picker_keyboard, time_picker_keyboard,
    day_picker_keyboard, time_picker_recurring_keyboard,
    recurring_list_keyboard, payment_approve_keyboard,
    booking_confirm_keyboard,
)
from i18n import LANGS, t, get_lang
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def is_admin(user_id):
    return user_id in ADMIN_IDS


def is_teacher_or_env(user_id):
    return user_id in TEACHER_IDS or is_teacher(user_id)


def _auto_register_teacher(uid, name="Teacher"):
    if uid in TEACHER_IDS and not is_teacher(uid):
        add_teacher(uid, name)


# ─── Photo handler for payment receipts ──────────────

async def handle_photo(update: Update, context):
    """Student sends payment receipt photo."""
    uid = update.effective_user.id
    lang = get_language(uid)

    # Check if user has a payment-pending booking
    booking = get_current_payment_for_user(uid)
    if not booking:
        await update.message.reply_text(t("no_good", lang))
        return

    # Get the largest photo (best quality)
    photo = update.message.photo[-1]
    file_id = photo.file_id

    result = submit_payment_receipt(booking["id"], uid, file_id)
    if not result:
        await update.message.reply_text(t("no_good", lang))
        return

    await update.message.reply_text(t("payment_received", lang))

    # Forward to check group
    group_msg_id = None
    if GROUP_CHECK_ID:
        try:
            gmsg = await context.bot.send_photo(
                chat_id=GROUP_CHECK_ID,
                photo=file_id,
                caption=f"💳 Chek\n👤 {result['student_name']}\n📅 {result['date']} {result['time']}\n👨‍🏫 {result['teacher_name']}",
            )
            group_msg_id = gmsg.message_id
            save_check_forward(booking["id"], GROUP_CHECK_ID, group_msg_id)
        except Exception as e:
            logger.error("Cannot forward to group %s: %s", GROUP_CHECK_ID, e)

    # Notify all admins
    admin_msg = t("payment_approve_admin", lang,
                  student=result["student_name"],
                  date=result["date"],
                  time=result["time"],
                  teacher=result["teacher_name"])

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_msg,
                reply_markup=payment_approve_keyboard(result["id"], lang),
            )
        except Exception as e:
            logger.error("Cannot notify admin %s: %s", admin_id, e)


# ─── Menu text handler ───────────────────────────────

async def handle_menu_text(update: Update, context):
    """Handle ReplyKeyboard menu button presses."""
    text = update.message.text
    uid = update.effective_user.id
    lang = get_language(uid)

    if text == t("menu_slots", lang):
        await slots_cmd(update, context)
    elif text == t("menu_mybookings", lang):
        await mybookings_cmd(update, context)
    elif text == t("menu_cancel", lang):
        await cancel_cmd(update, context)
    elif text in (t("menu_newslot", lang), t("menu_recurring", lang),
                  t("menu_myrecurring", lang), t("menu_myslots", lang)):
        if not is_admin(uid) and not is_teacher_or_env(uid):
            await update.message.reply_text(t("teacher_only", lang))
            return
        if not is_teacher(uid):
            _auto_register_teacher(uid, update.effective_user.full_name or "Teacher")

        if text == t("menu_newslot", lang):
            await update.message.reply_text(
                t("pick_date", lang),
                reply_markup=date_picker_keyboard(lang),
                parse_mode="Markdown",
            )
        elif text == t("menu_recurring", lang):
            await update.message.reply_text(
                t("pick_day", lang),
                reply_markup=day_picker_keyboard(lang),
                parse_mode="Markdown",
            )
        elif text == t("menu_myrecurring", lang):
            from db import get_recurring_patterns, DAY_NAMES_I18N
            patterns = get_recurring_patterns(uid)
            day_names = DAY_NAMES_I18N.get(lang, DAY_NAMES_I18N["uz"])
            if not patterns:
                await update.message.reply_text(t("no_recurring", lang))
                return
            msg = t("recurring_title", lang)
            for p in patterns:
                day_name = day_names.get(p["day_of_week"], str(p["day_of_week"]))
                msg += f"• {day_name} — {p['time']}\n"
            msg += t("recurring_delete_hint", lang)
            await update.message.reply_text(
                msg,
                reply_markup=recurring_list_keyboard(patterns, lang),
                parse_mode="Markdown",
            )
        elif text == t("menu_myslots", lang):
            await myslots_cmd(update, context)
    elif text == t("menu_addteacher", lang):
        if not is_admin(uid):
            await update.message.reply_text(t("admin_only", lang))
            return
        await update.message.reply_text(
            "📝 *O'qituvchi qo'shish* — quyidagi usullardan birini ishlating:\n\n"
            "1️⃣ O'qituvchining biror xabariga *reply* qilib `/addteacher Ismi` yozing\n"
            "2️⃣ `/addteacher @username Ismi` yozing\n"
            "3️⃣ `/addteacher <Telegram_ID> Ismi` yozing",
            parse_mode="Markdown",
        )
    elif text == t("menu_all_bookings", lang):
        if not is_admin(uid):
            await update.message.reply_text(t("admin_only", lang))
            return
        bookings = get_all_bookings()
        if not bookings:
            await update.message.reply_text(t("no_bookings_admin", lang))
            return
        msg = t("all_bookings_title", lang)
        for b in bookings:
            icon = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}.get(b["status"], "❓")
            pay_icon = {"payment_submitted": "💳", "payment_approved": "💵", "payment_rejected": "❌"}.get(b.get("payment_status", ""), "")
            msg += f"{icon}{pay_icon} {b['student_name']} → {b['teacher_name']} | {b['date']} {b['time']}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == t("menu_teachers", lang):
        if not is_admin(uid):
            await update.message.reply_text(t("admin_only", lang))
            return
        teachers = get_all_teachers()
        if not teachers:
            await update.message.reply_text(t("no_teachers", lang))
            return
        msg = t("all_teachers_title", lang)
        for teacher in teachers:
            uname = f" (@{teacher['username']})" if teacher.get('username') else ""
            msg += f"• {teacher['name']}{uname} — ID: `{teacher['telegram_id']}`\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif text == t("menu_pending_payments", lang):
        if not is_admin(uid):
            await update.message.reply_text(t("admin_only", lang))
            return
        payments = get_pending_payments()
        if not payments:
            await update.message.reply_text("📭 Hozircha tasdiqlanmagan to'lov yo'q.\n\n📭 No pending payments.\n\n📭 Нет ожидающих оплат.")
            return
        for p in payments:
            admin_msg = t("payment_approve_admin", lang,
                          student=p["student_name"],
                          date=p["date"],
                          time=p["time"],
                          teacher=p["teacher_name"])
            try:
                if p.get("payment_photo_id"):
                    await update.message.reply_photo(
                        photo=p["payment_photo_id"],
                        caption=admin_msg,
                        reply_markup=payment_approve_keyboard(p["id"], lang),
                    )
                else:
                    await update.message.reply_text(
                        admin_msg,
                        reply_markup=payment_approve_keyboard(p["id"], lang),
                    )
            except Exception as e:
                logger.error("Cannot show payment %s: %s", p["id"], e)
    elif text == t("menu_checksearch", lang):
        if not is_admin(uid):
            await update.message.reply_text(t("admin_only", lang))
            return
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 Bugungi", callback_data="check_today")],
            [InlineKeyboardButton("📆 Shu hafta", callback_data="check_week")],
            [InlineKeyboardButton("🗓 Shu oy", callback_data="check_month")],
        ])
        await update.message.reply_text(
            "🔍 Qaysi davrdagi cheklarni ko'rmoqchisiz?",
            reply_markup=kb,
        )


# ─── Language selection handler ──────────────────────

async def handle_lang_select(update: Update, context):
    """Called when user picks a language on the inline keyboard."""
    query = update.callback_query
    data = query.data
    uid = update.effective_user.id

    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        set_language(uid, lang)
        context.user_data["lang"] = lang
        await query.edit_message_text(t("lang_set", lang))
        # Now show the role-based menu
        await _show_menu(update, context, uid, lang)
        return

    # Fall through to unified handler
    await _unified_button_handler(update, context)


# ─── Show appropriate menu ──────────────────────────

async def _show_menu(update: Update, context, uid, lang):
    """Show the right menu based on role."""
    if is_admin(uid):
        await update.effective_message.reply_text(
            t("admin_welcome_title", lang) + "\n\n" +
            t("admin_welcome_desc", lang) + "\n\n" +
            t("admin_welcome_menu", lang),
            reply_markup=admin_reply_keyboard(lang),
            parse_mode="Markdown",
        )
    elif is_teacher_or_env(uid):
        if not is_teacher(uid):
            _auto_register_teacher(uid, update.effective_user.full_name or "Teacher")
        await update.effective_message.reply_text(
            t("teacher_welcome_title", lang) + "\n\n" +
            t("teacher_welcome_desc", lang),
            reply_markup=teacher_reply_keyboard(lang),
            parse_mode="Markdown",
        )
    else:
        await update.effective_message.reply_text(
            t("welcome_title", lang) + "\n\n" +
            t("welcome_desc", lang) + "\n\n" +
            t("welcome_how", lang) + "\n" +
            t("welcome_step1", lang) + "\n" +
            t("welcome_step2", lang) + "\n" +
            t("welcome_step3", lang) + "\n" +
            t("welcome_step4", lang) + "\n" +
            t("welcome_step5", lang),
            reply_markup=student_reply_keyboard(lang),
            parse_mode="Markdown",
        )


# ─── Start command ──────────────────────────────────

async def start_cmd(update: Update, context):
    """Start with language selection (shows every time for consistency)."""
    uid = update.effective_user.id
    lang = get_language(uid)
    context.user_data["lang"] = lang

    # Also show lang picker in case user wants to change
    await update.message.reply_text(
        "🇺🇿 Tilni tanlang / 🇬🇧 Choose language / 🇷🇺 Выберите язык",
        reply_markup=lang_picker_keyboard(),
    )


# ─── Unified button handler ─────────────────────────

async def _unified_button_handler(update: Update, context):
    """Central inline button handler."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    uid = user.id
    lang = get_language(uid)

    # Payment approval/rejection by admin
    if data.startswith("payok_") or data.startswith("payno_"):
        if not is_admin(uid):
            await query.answer(t("admin_only", lang), show_alert=True)
            return
        booking_id = int(data.split("_")[1])

        if data.startswith("payok_"):
            result = approve_payment(booking_id, uid)
            if not result:
                await query.answer("⚠️ Bandlov topilmadi", show_alert=True)
                return
            # Notify student
            msg = t("payment_approve_student", result.get("student_lang", lang))
            try:
                await context.bot.send_message(
                    chat_id=result["student_telegram_id"],
                    text=msg,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error("Cannot notify student %s: %s", result["student_telegram_id"], e)
            await query.edit_message_caption(
                caption=f"✅ {result['student_name']} — To'lov tasdiqlandi!",
            )
        else:  # payno_
            result = reject_payment(booking_id, uid)
            if not result:
                await query.answer("⚠️ Bandlov topilmadi", show_alert=True)
                return
            # Notify student
            msg = t("payment_reject_student", result.get("student_lang", lang))
            try:
                await context.bot.send_message(
                    chat_id=result["student_telegram_id"],
                    text=msg,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error("Cannot notify student %s: %s", result["student_telegram_id"], e)
            await query.edit_message_caption(
                caption=f"❌ {result['student_name']} — To'lov rad etildi!",
            )
        await query.answer()
        return

    # Booking confirm/reject by teacher
    if data.startswith("confirm_") or data.startswith("reject_"):
        if not is_teacher_or_env(uid):
            await query.answer(t("teacher_only", lang), show_alert=True)
            return
        booking_id = int(data.split("_")[1])

        if data.startswith("confirm_"):
            from db import confirm_booking as _confirm
            result = _confirm(booking_id, uid)
            if not result:
                await query.answer("⚠️ Bandlov topilmadi", show_alert=True)
                return
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(f"✅ Bandlov tasdiqlandi!")
            try:
                await context.bot.send_message(
                    chat_id=result["student_telegram_id"],
                    text=t("booking_confirmed_student", lang, date="...", time="...", teacher="..."),
                )
            except Exception:
                pass
        else:  # reject_
            from db import reject_booking as _reject
            result = _reject(booking_id, uid)
            if not result:
                await query.answer("⚠️ Bandlov topilmadi", show_alert=True)
                return
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(f"❌ Bandlov rad etildi!")
        await query.answer()
        return

    # Add-slot flow
    if data.startswith("addslot_"):
        if not is_admin(uid) and not is_teacher_or_env(uid):
            await query.answer(t("teacher_only", lang), show_alert=True)
            return
        if not is_teacher(uid):
            _auto_register_teacher(uid, user.full_name or "Teacher")

        if data == "addslot_pick_date":
            await query.edit_message_text(
                t("pick_date", lang),
                reply_markup=date_picker_keyboard(lang),
                parse_mode="Markdown",
            )
        elif data.startswith("addslot_date_"):
            selected_date = data.replace("addslot_date_", "")
            await query.edit_message_text(
                t("pick_time", lang, date=selected_date),
                reply_markup=time_picker_keyboard(selected_date, lang),
                parse_mode="Markdown",
            )
        elif data.startswith("addslot_time_"):
            parts = data.replace("addslot_time_", "", 1)
            idx = parts.rfind("_")
            selected_date = parts[:idx]
            selected_time = parts[idx + 1:]
            add_slot(uid, selected_date, selected_time)
            text = t("slot_added", lang, date=selected_date, time=selected_time)
            text += "\n\n" + t("add_more", lang)
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ " + t("yes_add_more", lang), callback_data="addslot_pick_date"),
                    InlineKeyboardButton("❌ " + t("no_back", lang), callback_data="menu_back"),
                ]
            ])
            try:
                await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
            except Exception:
                await update.effective_message.reply_text(text, reply_markup=kb, parse_mode="Markdown")
        await query.answer()
        return

    # Recurring pattern flow
    if data.startswith("recur_"):
        if not is_admin(uid) and not is_teacher_or_env(uid):
            await query.answer(t("teacher_only", lang), show_alert=True)
            return
        if not is_teacher(uid):
            _auto_register_teacher(uid, user.full_name or "Teacher")

        if data == "recur_pick_day":
            await query.edit_message_text(
                t("pick_day", lang),
                reply_markup=day_picker_keyboard(lang),
                parse_mode="Markdown",
            )
        elif data.startswith("recur_day_"):
            day_of_week = int(data.replace("recur_day_", ""))
            from db import DAY_NAMES_I18N
            day_names = DAY_NAMES_I18N.get(lang, DAY_NAMES_I18N["uz"])
            day_name = day_names.get(day_of_week, str(day_of_week))
            await query.edit_message_text(
                t("pick_time", lang, date=day_name),
                reply_markup=time_picker_recurring_keyboard(day_of_week, lang),
                parse_mode="Markdown",
            )
        elif data.startswith("recur_time_"):
            parts = data.replace("recur_time_", "", 1)
            idx = parts.find("_")
            day_of_week = int(parts[:idx])
            selected_time = parts[idx + 1:]
            from db import add_recurring_pattern, generate_slots_from_patterns, DAY_NAMES_I18N
            day_names = DAY_NAMES_I18N.get(lang, DAY_NAMES_I18N["uz"])
            day_name = day_names.get(day_of_week, str(day_of_week))
            add_recurring_pattern(uid, day_of_week, selected_time)
            count = generate_slots_from_patterns(uid, weeks=4)
            text = t("recurring_added", lang, day=day_name, time=selected_time, count=count)
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=day_picker_keyboard(lang),
            )
        elif data.startswith("recur_del_"):
            pattern_id = int(data.replace("recur_del_", ""))
            from db import remove_recurring_pattern, get_recurring_patterns, DAY_NAMES_I18N
            remove_recurring_pattern(pattern_id, uid)
            patterns = get_recurring_patterns(uid)
            day_names = DAY_NAMES_I18N.get(lang, DAY_NAMES_I18N["uz"])
            if not patterns:
                await query.edit_message_text(t("recurring_deleted", lang), parse_mode="Markdown")
            else:
                msg = t("recurring_title", lang)
                for p in patterns:
                    day_name = day_names.get(p["day_of_week"], str(p["day_of_week"]))
                    msg += f"• {day_name} — {p['time']}\n"
                msg += t("recurring_delete_hint", lang)
                await query.edit_message_text(
                    msg,
                    reply_markup=recurring_list_keyboard(patterns, lang),
                    parse_mode="Markdown",
                )
        await query.answer()
        return

    # Menu back (after slot created etc.)
    if data == "menu_back":
        uid = query.from_user.id
        lang = get_language(uid)
        await _show_menu(update, context, uid, lang)
        await query.answer()
        return

    # Fall through to student button handler
    await button_handler(update, context)


# ─── Main ────────────────────────────────────────────

def main():
    init_db()

    # Sync from Google Sheets on startup
    t_count, s_count = sync_from_sheets()
    if t_count is not None:
        logger.info(f"✅ Google Sheets'dan yuklandi: {t_count} o'qituvchi, {s_count} slot")
    else:
        logger.info("⚠️ Google Sheets ulanmadi — bo'sh boshlandi")

    app = Application.builder().token(BOT_TOKEN).build()

    # Student commands
    app.add_handler(CommandHandler("start", start_cmd))
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

    # Photo handler for payment receipts
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Check search command (admin only)
    async def checkquery_cmd(update: Update, context):
        uid = update.effective_user.id
        lang = get_language(uid)
        if uid not in ADMIN_IDS:
            await update.message.reply_text(t("admin_only", lang))
            return
        args = context.args
        if not args:
            # No args: show inline buttons for quick periods
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Bugungi", callback_data="check_today")],
                [InlineKeyboardButton("📆 Shu hafta", callback_data="check_week")],
                [InlineKeyboardButton("🗓 Shu oy", callback_data="check_month")],
            ])
            await update.message.reply_text("🔍 Qaysi davrdagi cheklarni ko'rmoqchisiz?", reply_markup=kb)
            return
        query_text = " ".join(args).strip()
        results = find_checks_by_query(query_text)
        await _send_check_results(update, context, uid, results, query_text)

    app.add_handler(CommandHandler("checkquery", checkquery_cmd))
    app.add_handler(CommandHandler("checkq", checkquery_cmd))  # Short alias

    # Check period handler (today/week/month)
    async def handle_check_period(update: Update, context):
        query = update.callback_query
        await query.answer()
        uid = query.from_user.id
        lang = get_language(uid)
        if uid not in ADMIN_IDS:
            await query.message.reply_text(t("admin_only", lang))
            return
        import datetime
        today = datetime.date.today()
        action = query.data
        if action == "check_today":
            period, results = "bugungi", _get_check_results(text_query=today.isoformat())
        elif action == "check_week":
            end = today + datetime.timedelta(days=7)
            period, results = "shu haftadagi", _get_check_results(
                date_from=today.isoformat(), date_to=end.isoformat(),
            )
        elif action == "check_month":
            period, results = "shu oydagi", _get_check_results(month=today.strftime("%Y-%m"))
        else:
            return
        if not results:
            await query.message.reply_text(f"📭 {period} chek topilmadi.")
            return
        for r in results:
            try:
                await context.bot.copy_message(
                    chat_id=uid,
                    from_chat_id=r["chat_id"],
                    message_id=r["message_id"],
                    caption=f"👤 {r['student_name']} | 📅 {r['date']} | {r['time']} | {r['teacher_name']}",
                )
            except Exception as e:
                await query.message.reply_text(
                    f"👤 {r['student_name']} | 📅 {r['date']} | {r['time']} | {r['teacher_name']}\n⚠️ Rasmni qayta yuborib bo'lmadi"
                )

    app.add_handler(CallbackQueryHandler(handle_check_period, pattern=r"^check_"))

    def _get_check_results(text_query=None, month=None, date_from=None, date_to=None):
        """Wrapper for find_checks_by_query with extra params."""
        return find_checks_by_query(
            query=text_query,
            month=month,
            date_from=date_from,
            date_to=date_to,
        )

    async def _send_check_results(update, context, uid, results, query_text):
        if not results:
            await update.message.reply_text(f"📭 '{query_text}' bo'yicha chek topilmadi.")
            return
        for r in results:
            try:
                await context.bot.copy_message(
                    chat_id=uid,
                    from_chat_id=r["chat_id"],
                    message_id=r["message_id"],
                    caption=f"👤 {r['student_name']} | 📅 {r['date']} | {r['time']} | {r['teacher_name']}",
                )
            except Exception as e:
                await update.message.reply_text(
                    f"👤 {r['student_name']} | 📅 {r['date']} | {r['time']} | {r['teacher_name']}\n⚠️ Rasmni qayta yuborib bo'lmadi"
                )

    # Language selection + unified callback handler
    app.add_handler(CallbackQueryHandler(handle_lang_select))

    # ReplyKeyboard menu handler
    all_menu_texts = []
    for lang_code in ["uz", "en", "ru"]:
        all_menu_texts.extend([
            t("menu_slots", lang_code),
            t("menu_mybookings", lang_code),
            t("menu_cancel", lang_code),
            t("menu_newslot", lang_code),
            t("menu_myslots", lang_code),
            t("menu_recurring", lang_code),
            t("menu_myrecurring", lang_code),
            t("menu_addteacher", lang_code),
            t("menu_teachers", lang_code),
            t("menu_all_bookings", lang_code),
            t("menu_pending_payments", lang_code),
            t("menu_checksearch", lang_code),
        ])

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Text(all_menu_texts),
        handle_menu_text,
    ))

    logger.info("✅ IELTS Mock Booking Bot ishga tushdi! (3 til, to'lov cheki, Sheets sync)")

    retries = 0
    while True:
        try:
            app.run_polling()
        except Conflict:
            retries += 1
            wait = min(5 * retries, 30)
            logger.warning(f"⚠️ Conflict — {wait}s kutib qayta urinish (#{retries})...")
            time.sleep(wait)
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 Bot to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"❌ Xato: {e}")
            break


if __name__ == "__main__":
    main()
