from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN
from db import init_db
from handlers.student import (
    start, slots_cmd, mybookings_cmd, cancel_cmd, button_handler,
)
from handlers.teacher import addslot_cmd, myslots_cmd, removeslot_cmd
from handlers.admin import addteacher_cmd, removeteacher_cmd


async def handle_menu_text(update: Update, context):
    """Handle ReplyKeyboard menu button presses."""
    text = update.message.text

    if text == "📋 Mavjud slotlar":
        await slots_cmd(update, context)
    elif text == "📅 Mening bandlovlarim":
        await mybookings_cmd(update, context)
    elif text == "❌ Bandlovni bekor qilish":
        await cancel_cmd(update, context)
    # ignore other plain text


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

    # Inline button handler (covers all callbacks)
    app.add_handler(CallbackQueryHandler(button_handler))

    # ReplyKeyboard menu button handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND &
        (filters.Text("📋 Mavjud slotlar") |
         filters.Text("📅 Mening bandlovlarim") |
         filters.Text("❌ Bandlovni bekor qilish")),
        handle_menu_text,
    ))

    print("✅ IELTS Mock Booking Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
