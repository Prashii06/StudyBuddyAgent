import os
from dotenv import load_dotenv

load_dotenv()

APP_CONFIG = {
    "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    "temperature": float(os.getenv("TEMPERATURE", "0.2")),
}

API_KEYS = {
    "gemini_api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
}