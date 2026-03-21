from fastapi import APIRouter
from event_queue import EVENT_QUEUE

import asyncio
import json


router = APIRouter()

LEADERBOARD_CACHE = {}
COMMANDS_CACHE = {}
SETTINGS_CACHE = {}
TIMED_CACHE = {}

# =========================
# 💬 ADD CUSTOM COMMAND
# =========================
@router.post("/command/add")
async def add_command(data: dict):

    # normalize command
    data["command"] = data["command"].strip().lower()
    data["response"] = data["response"].strip()

    EVENT_QUEUE.append({
        "type": "command.add",
        "event": data
    })

    print("📨 Command event queued:", data)

    return {"success": True}


# =========================
# 📜 GET COMMAND LIST
# =========================
@router.get("/commands")
async def get_commands(channel: str):

    # clear old cache
    COMMANDS_CACHE.pop(channel, None)

    EVENT_QUEUE.append({
        "type": "commands.list",
        "event": {"channel": channel}
    })

    print("📜 Command list requested:", channel)

    # wait up to ~6 seconds
    for _ in range(60):
        if channel in COMMANDS_CACHE:
            return COMMANDS_CACHE[channel]
        await asyncio.sleep(0.1)

    return []


# =========================
# 🏆 LEADERBOARD REQUEST
# =========================
@router.get("/leaderboard")
async def leaderboard(channel: str):

    # clear old cache
    LEADERBOARD_CACHE.pop(channel, None)

    EVENT_QUEUE.append({
        "type": "leaderboard.request",
        "event": {"channel": channel}
    })

    print("📊 Leaderboard request queued:", channel)

    # wait up to ~6 seconds for SparkedHost
    for _ in range(60):
        if channel in LEADERBOARD_CACHE:
            return LEADERBOARD_CACHE[channel]
        await asyncio.sleep(0.1)

    return []


# =========================
# 📥 LEADERBOARD RESPONSE
# =========================
@router.post("/internal/leaderboard")
async def leaderboard_response(data: dict):

    channel = data["channel"]

    LEADERBOARD_CACHE[channel] = data["data"]

    print("📊 Leaderboard updated for", channel)

    return {"ok": True}


# =========================
# 📥 COMMAND RESPONSE
# =========================
@router.post("/internal/commands")
async def commands_response(data: dict):

    channel = data["channel"]

    commands = data["data"]

    if isinstance(commands, str):
        commands = json.loads(commands)

    COMMANDS_CACHE[channel] = commands

    print("📜 Commands updated for", channel)

    return {"ok": True}


# =========================
# 🗑 DELETE COMMAND
# =========================
@router.post("/command/delete")
async def delete_command(data: dict):

    EVENT_QUEUE.append({
        "type": "command.delete",
        "event": data
    })

    print("🗑 Command delete queued:", data)

    return {"success": True}


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

@router.post("/medals/set")
async def set_medals(data: dict):

    EVENT_QUEUE.append({
        "type": "medals.set",
        "event": data
    })

    print("🏅 Medal settings queued:", data)

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

@router.post("/internal/settings")
async def settings_response(data: dict):

    channel = data["channel"]

    SETTINGS_CACHE[channel] = data["data"]

    print("⚙️ Settings updated for", channel)

    return {"ok": True}

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

@router.get("/timed/list")
async def timed_list(channel: str):

    TIMED_CACHE.pop(channel, None)

    EVENT_QUEUE.append({
        "type": "timed.list",
        "event": {"channel": channel}
    })

    for _ in range(60):
        if channel in TIMED_CACHE:  # ✅ CORRECT
            return TIMED_CACHE[channel]
        await asyncio.sleep(0.1)

    return []

@router.post("/internal/timed")
async def timed_response(data: dict):

    channel = data["channel"]

    TIMED_CACHE[channel] = data["data"]

    print("⏰ Timed updated for", channel)

    return {"ok": True}


@router.get("/settings")
async def get_settings(channel: str):

    SETTINGS_CACHE.pop(channel, None)

    EVENT_QUEUE.append({
        "type": "settings.request",
        "event": {"channel": channel}
    })

    for _ in range(60):
        if channel in SETTINGS_CACHE:
            return SETTINGS_CACHE[channel]
        await asyncio.sleep(0.1)

    return {
        "medals_enabled": 1
    }