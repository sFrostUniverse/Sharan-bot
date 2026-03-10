from fastapi import APIRouter
from event_queue import EVENT_QUEUE

router = APIRouter()

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
        "event": {
            "channel": channel
        }
    })

    print("📊 Leaderboard request queued:", channel)

    return {"status": "queued"}

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