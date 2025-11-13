import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")

# Google Sheets настройки
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")

# Папки для сохранения данных
DATA_DIR = "data"
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")

# Создаем папки если их нет
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

