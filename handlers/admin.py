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

    # Use from reply if available, otherwise accept /addteacher @username Ism
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        name = " ".join(context.args) if context.args else target.full_name
        username = f"@{target.username}" if target.username else ""
        add_teacher(target.id, name, username)
        await update.message.reply_text(
            f"✅ O'qituvchi qo'shildi: {name} ({username})\n"
            f"Telegram ID: `{target.id}`",
            parse_mode="Markdown",
        )
        return

    # Direct mode: /addteacher @username Ism  or  /addteacher 123456 Ism
    if not context.args:
        await update.message.reply_text(
            "📝 O'qituvchi qo'shish uchun:\n\n"
            "• O'qituvchining xabariga reply qilib `/addteacher Ism` yozing\n"
            "• Yoki `/addteacher @username Ism`\n"
            "• Yoki `/addteacher 123456789 Ism` (Telegram ID)\n\n"
            "Masalan: `/addteacher @karim Karimboy`",
            parse_mode="Markdown",
        )
        return

    # Parse: first arg is @username or numeric ID
    first_arg = context.args[0]
    name = " ".join(context.args[1:]) if len(context.args) > 1 else first_arg.lstrip("@")

    if first_arg.startswith("@"):
        # By username - we need to look up ID (approximate)
        username = first_arg
        # We can't look up by @username without a message from them
        # So store with username only, ID=0 as placeholder
        add_teacher(0, name, username)
        await update.message.reply_text(
            f"✅ O'qituvchi saqlandi: {name} ({username})\n"
            "⚠️ ID aniqlash uchun o'qituvchi botga xabar yuborishi kerak."
        )
    elif first_arg.isdigit():
        tid = int(first_arg)
        add_teacher(tid, name)
        await update.message.reply_text(
            f"✅ O'qituvchi qo'shildi: {name}\n"
            f"Telegram ID: `{tid}`",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "❌ Format noto'g'ri. `/addteacher @username Ism` yoki `/addteacher 123456 Ism`\n"
            "Masalan: `/addteacher @karim Karimboy`",
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
