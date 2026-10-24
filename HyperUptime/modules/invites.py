from datetime import datetime, timezone, timedelta
from .storage import load_data, save_data


MIN_ACCOUNT_AGE_DAYS = 21


def is_account_old_enough(created_at: datetime) -> bool:
    now = datetime.now(timezone.utc)
    return now - created_at >= timedelta(days=MIN_ACCOUNT_AGE_DAYS)


def get_invites(user_id: int) -> int:
    data = load_data()
    return int(data["invites"].get(str(user_id), 0))


def change_invites(user_id: int, amount: int):
    data = load_data()
    key = str(user_id)
    data["invites"][key] = max(
        0, int(data["invites"].get(key, 0)) + amount
    )
    save_data(data)
    return data["invites"][key]