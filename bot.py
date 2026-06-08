from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from config import BOT_TOKEN
from db import init_db
from handlers.student import (
    start, slots_cmd, mybookings_cmd, cancel_cmd, button_handler,
)
from handlers.teacher import addslot_cmd, myslots_cmd, removeslot_cmd
from handlers.admin import addteacher_cmd, removeteacher_cmd


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

    print("✅ IELTS Mock Booking Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
