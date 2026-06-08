from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_IDS
from db import add_teacher, remove_teacher_db


def is_admin(user_id):
    return user_id in ADMIN_IDS


async def addteacher_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Faqat admin uchun.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "📝 O'qituvchining xabariga reply qilib `/addteacher Ismi` yozing."
        )
        return

    target = update.message.reply_to_message.from_user
    name = " ".join(context.args) if context.args else target.full_name
    username = f"@{target.username}" if target.username else ""

    add_teacher(target.id, name, username)
    await update.message.reply_text(
        f"✅ O'qituvchi qo'shildi: {name} ({username})\n"
        f"Telegram ID: `{target.id}`",
        parse_mode="Markdown",
    )


async def removeteacher_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Faqat admin uchun.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "📝 O'qituvchining xabariga reply qilib `/removeteacher` yozing."
        )
        return

    target = update.message.reply_to_message.from_user
    remove_teacher_db(target.id)
    await update.message.reply_text(f"✅ O'qituvchi o'chirildi: {target.full_name}")
