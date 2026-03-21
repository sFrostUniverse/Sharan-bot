import json
import os
import time
import random
from typing import Dict

POINTS_FILE = "data/points.json"
DAILY_COOLDOWN = 86400  # 24 hours

os.makedirs("data", exist_ok=True)

# =========================
# 🧠 STATE
# =========================
points: Dict[str, int] = {}
last_daily: Dict[str, float] = {}


# =========================
# 💾 STORAGE
# =========================
def load_points():
    global points, last_daily
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            data = json.load(f)
            points = data.get("points", {})
            last_daily = data.get("daily", {})


def save_points():
    with open(POINTS_FILE, "w") as f:
        json.dump(
            {
                "points": points,
                "daily": last_daily,
            },
            f,
            indent=2,
        )


# =========================
# 🎯 CORE LOGIC
# =========================
def get_points(user: str) -> int:
    return points.get(user, 0)


def add_points(user: str, amount: int):
    points[user] = get_points(user) + amount
    save_points()


def can_claim_daily(user: str) -> bool:
    last = last_daily.get(user, 0)
    return time.time() - last >= DAILY_COOLDOWN


def claim_daily(user: str) -> int | None:
    if not can_claim_daily(user):
        return None

    reward = 25
    add_points(user, reward)
    last_daily[user] = time.time()
    save_points()
    return reward


def gamble_points(user: str, amount: int) -> int | None:
    if amount <= 0:
        return None

    if get_points(user) < amount:
        return None

    win = random.choice([True, False])

    if win:
        add_points(user, amount)
        return amount
    else:
        add_points(user, -amount)
        return -amount