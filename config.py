import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "1054482233").split(",") if x]
# Comma-separated teacher Telegram IDs
_teacher_env = os.getenv("TEACHER_IDS", "1054482233,8509971923")
TEACHER_IDS = [int(x) for x in _teacher_env.split(",") if x.strip()]
TEACHER_NAMES = {
    1054482233: "Karimboy (Admin)",
    8509971923: "Test Teacher",
}
GROUP_CHECK_ID = int(os.getenv("GROUP_CHECK_ID", "-5291911618"))  # Chek rasmlari tushadigan guruh

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment")
