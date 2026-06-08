"""Admin handlers — add/remove teachers, payment management."""
from telegram import Update
from telegram.ext import ContextTypes

from db import (
    is_teacher, add_teacher, get_language,
)
from config import ADMIN_IDS
from i18n import t


def is_admin(user_id):
    return user_id in ADMIN_IDS


async def addteacher_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)

    if not is_admin(uid):
        await update.message.reply_text(t("admin_only", lang))
        return

    args = context.args
    target_name = ""
    target_id = None
    target_username = ""

    # Try reply
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_name = " ".join(args) if args else update.message.reply_to_message.from_user.full_name or "Teacher"
        target_username = update.message.reply_to_message.from_user.username or ""
    elif len(args) >= 1:
        if args[0].startswith("@"):
            target_username = args[0].lstrip("@")
            target_name = " ".join(args[1:]) if len(args) > 1 else target_username
        elif args[0].isdigit():
            target_id = int(args[0])
            target_name = " ".join(args[1:]) if len(args) > 1 else "Teacher"
        else:
            await update.message.reply_text(
                "📝 Format: `/addteacher @username Ismi` yoki reply qilib `/addteacher Ismi`",
                parse_mode="Markdown",
            )
            return

    if target_id:
        add_teacher(target_id, target_name, target_username)
        await update.message.reply_text(
            t("added_teacher", lang) + f" — {target_name}",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "⚠️ Avval botga xabar yozgan o'qituvchining xabariga reply qiling, yoki Telegram ID sini bering."
        )


async def removeteacher_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_language(uid)

    if not is_admin(uid):
        await update.message.reply_text(t("admin_only", lang))
        return

    from db import remove_teacher_db, get_all_teachers

    args = context.args
    if not args or not args[0].isdigit():
        teachers = get_all_teachers()
        msg = t("all_teachers_title", lang)
        for teacher in teachers:
            msg += f"/removeteacher {teacher['telegram_id']} — {teacher['name']}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    tid = int(args[0])
    remove_teacher_db(tid)
    await update.message.reply_text(f"🗑 O'qituvchi o'chirildi: {tid}")
