from fastapi import APIRouter
from event_queue import EVENT_QUEUE

import asyncio

router = APIRouter()

LEADERBOARD_CACHE = {}
# =========================
# 💬 ADD CUSTOM COMMAND
# =========================
@router.post("/command/add")
async def add_command(data: dict):

    EVENT_QUEUE.append({
        "type": "command.add",
        "event": data
    })

    print("📨 Command event queued:", data)

    return {"success": True}

# =========================
# 🏆 LEADERBOARD REQUEST
# =========================
@router.get("/leaderboard")
async def leaderboard(channel: str):

    EVENT_QUEUE.append({
        "type": "leaderboard.request",
        "event": {"channel": channel}
    })

    print("📊 Leaderboard request queued:", channel)

    # wait up to 2 seconds for SparkedHost to respond
    for _ in range(20):
        if channel in LEADERBOARD_CACHE:
            return LEADERBOARD_CACHE[channel]
        await asyncio.sleep(0.1)

    return []



@router.post("/internal/leaderboard")
async def leaderboard_response(data: dict):

    channel = data["channel"]

    LEADERBOARD_CACHE[channel] = data["data"]

    print("📊 Leaderboard updated for", channel)

    return {"ok": True}

# =========================
# 💰 SET CURRENCY
# =========================
@router.post("/currency/set")
async def set_currency(data: dict):

    EVENT_QUEUE.append({
        "type": "currency.set",
        "event": data
    })

    print("💰 Currency event queued:", data)

    return {"success": True}

@router.post("/economy/save")
async def save_economy(data: dict):

    EVENT_QUEUE.append({
        "type": "economy.save",
        "event": data
    })

    print("💰 Economy settings queued:", data)

    return {"success": True}

# =========================
# ⚙️ POINT SETTINGS
# =========================
@router.post("/points/settings")
async def set_points_settings(data: dict):

    EVENT_QUEUE.append({
        "type": "points.settings",
        "event": data
    })

    print("⚙️ Points settings event queued:", data)

    return {"success": True}


# =========================
# ⏰ ADD TIMED MESSAGE
# =========================
@router.post("/timed/add")
async def add_timed_message(data: dict):

    EVENT_QUEUE.append({
        "type": "timed.add",
        "event": data
    })

    print("⏰ Timed message event queued:", data)

    return {"success": True}