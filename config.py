import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "1054482233").split(",") if x]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment")
