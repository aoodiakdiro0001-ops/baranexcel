"""Free-quota + paid-credits store (JSON file, no database needed)."""
import json
import os

FREE_LIMIT = 3


def _load(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def check_allow(path, user_id):
    """Returns (allowed: bool, remaining_free: int, credits: int)."""
    data = _load(path)
    u = data.get(str(user_id), {"free_used": 0, "credits": 0})
    if u.get("credits", 0) > 0:
        return True, 0, u["credits"]
    if u.get("free_used", 0) < FREE_LIMIT:
        return True, FREE_LIMIT - u["free_used"] - 1, 0
    return False, 0, 0


def consume(path, user_id):
    data = _load(path)
    u = data.setdefault(str(user_id), {"free_used": 0, "credits": 0})
    if u.get("credits", 0) > 0:
        u["credits"] -= 1
    else:
        u["free_used"] = u.get("free_used", 0) + 1
    _save(path, data)


def add_credits(path, user_id, n):
    data = _load(path)
    u = data.setdefault(str(user_id), {"free_used": 0, "credits": 0})
    u["credits"] = u.get("credits", 0) + int(n)
    _save(path, data)
    return u["credits"]
