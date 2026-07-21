"""Bot configuration loaded from .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# Comma-separated Telegram user ids that may use admin commands (/stats, /reload)
ADMIN_IDS: set[int] = {
    int(x) for x in os.getenv("ADMIN_IDS", "").replace(";", ",").split(",") if x.strip().isdigit()
}

# Where the .svm setup library lives: setups/<TrackFolder>/[<Author>/]file.svm
SETUPS_DIR: Path = Path(os.getenv("SETUPS_DIR", BASE_DIR / "setups"))

# Where per-user data (language choice) and download stats are stored
DATA_DIR: Path = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

# How long (seconds) a library scan is cached before the folder is re-checked.
# Small value = new setup files appear in the bot almost instantly.
LIBRARY_CACHE_TTL: int = int(os.getenv("LIBRARY_CACHE_TTL", "15"))
