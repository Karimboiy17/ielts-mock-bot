"""Teacher handlers — slot management, 3-language."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from db import (
    is_teacher, add_slot, get_teacher_slots, remove_slot, add_teacher, get_language,
)
from config import ADMIN_IDS, TEACHER_IDS
from i18n import t


def is_admin(user_id):
    return user_id in ADMIN_IDS


def _ensure_teacher(uid, name="Admin"):
    if uid in TEACHER_IDS and not is_teacher(uid):
        add_teacher(uid, name)
        return True
    return False


async def addslot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)

    if not is_teacher(uid) and not is_admin(uid):
        await update.message.reply_text(t("teacher_only", lang))
        return

    if is_admin(uid):
        name = update.effective_user.full_name or "Admin"
        _ensure_teacher(uid, name)

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📝 Format: `/addslot YYYY-MM-DD HH:MM`\nMasalan: `/addslot 2026-06-15 14:00`",
            parse_mode="Markdown",
        )
        return

    date, time = args[0], args[1]
    add_slot(uid, date, time)
    await update.message.reply_text(f"✅ Slot qo'shildi: {date} {time}")


async def myslots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)

    if not is_teacher(uid) and not is_admin(uid):
        await update.message.reply_text(t("teacher_only", lang))
        return

    if is_admin(uid):
        _ensure_teacher(uid, update.effective_user.full_name or "Admin")

    slots = get_teacher_slots(uid)
    if not slots:
        await update.message.reply_text(t("no_slots", lang))
        return

    text = t("your_slots", lang)
    buttons = []
    for s in slots:
        st = t("status_available", lang) if s["status"] == "available" else t("status_booked", lang)
        if s["status"] == "pending":
            st = t("status_pending", lang)
        text += f"• {s['date']} {s['time']} — {st}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def removeslot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)

    if not is_teacher(uid) and not is_admin(uid):
        await update.message.reply_text(t("teacher_only", lang))
        return

    if is_admin(uid):
        _ensure_teacher(uid, update.effective_user.full_name or "Admin")

    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("📝 `/removeslot ID` — ID ni ko'rish uchun `/myslots`")
        return

    slot_id = int(args[0])
    remove_slot(slot_id, uid)
    await update.message.reply_text(f"🗑 Slot o'chirildi: {slot_id}")
