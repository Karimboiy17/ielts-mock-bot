from telegram import Update
from telegram.ext import ContextTypes

from db import is_teacher, add_slot, get_teacher_slots, remove_slot


async def addslot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_teacher(update.effective_user.id):
        await update.message.reply_text("⛔ Siz o'qituvchi emassiz.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📝 Format: `/addslot YYYY-MM-DD HH:MM`\n"
            "Masalan: `/addslot 2026-06-15 14:00`",
            parse_mode="Markdown",
        )
        return

    date, time = args[0], args[1]
    add_slot(update.effective_user.id, date, time)
    await update.message.reply_text(f"✅ Slot qo'shildi: {date} {time}")


async def myslots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_teacher(update.effective_user.id):
        await update.message.reply_text("⛔ Siz o'qituvchi emassiz.")
        return

    slots = get_teacher_slots(update.effective_user.id)
    if not slots:
        await update.message.reply_text("📭 Sizda hozircha slot yo'q.")
        return

    msg = "*📅 Sizning slotlaringiz:*\n\n"
    for s in slots:
        if s["status"] == "available":
            icon = "🟢"
        elif s["status"] == "pending":
            icon = "🟡"
        elif s["status"] == "booked":
            icon = "🔴"
        else:
            icon = "⚪"

        student = f" — {s['student_name']}" if s["student_name"] else ""
        msg += f"{icon} `{s['date']}` `{s['time']}`{student} (ID: {s['id']})\n"
    msg += "\n🟢=Bo'sh  🟡=Kutilmoqda  🔴=Band"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def removeslot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_teacher(update.effective_user.id):
        await update.message.reply_text("⛔ Siz o'qituvchi emassiz.")
        return

    if not context.args:
        await update.message.reply_text(
            "📝 Format: `/removeslot <slot_id>`\n"
            "Slot ID larni ko'rish uchun /myslots"
        )
        return

    slot_id = int(context.args[0])
    remove_slot(slot_id, update.effective_user.id)
    await update.message.reply_text(f"✅ Slot #{slot_id} o'chirildi.")
