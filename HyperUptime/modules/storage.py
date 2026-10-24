import json
import asyncio
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database.json"
_lock = asyncio.Lock()

DEFAULT_DATA = {
    "users": {},
    "invites": {},
    "bot_slots": {},
    "tracked_urls": {},
    "invite_uses": {}
}


def load_data():
    if not DB_PATH.exists():
        save_data(DEFAULT_DATA)
    try:
        with DB_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        for key, value in DEFAULT_DATA.items():
            data.setdefault(key, value.copy())
        return data
    except (json.JSONDecodeError, OSError):
        return {key: value.copy() for key, value in DEFAULT_DATA.items()}


def save_data(data):
    temp_path = DB_PATH.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temp_path.replace(DB_PATH)


async def update_data(callback):
    async with _lock:
        data = load_data()
        result = callback(data)
        save_data(data)
        return result