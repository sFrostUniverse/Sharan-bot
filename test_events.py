from fastapi import APIRouter
from event_queue import EVENT_QUEUE

router = APIRouter(prefix="/test")


# =========================
# 💜 FOLLOW
# =========================
@router.get("/follow")
async def test_follow(channel: str = "itsfrosea", user: str = "test_user"):

    EVENT_QUEUE.append({
        "type": "channel.follow",
        "event": {
            "broadcaster_user_login": channel,
            "user_name": user
        }
    })

    return {"queued": "follow event"}


# =========================
# ⭐ SUB
# =========================
@router.get("/sub")
async def test_sub(channel: str = "itsfrosea", user: str = "test_user"):

    EVENT_QUEUE.append({
        "type": "channel.subscribe",
        "event": {
            "broadcaster_user_login": channel,
            "user_name": user,
            "tier": "1"
        }
    })

    return {"queued": "sub event"}


# =========================
# 💎 CHEER
# =========================
@router.get("/cheer")
async def test_cheer(channel: str = "itsfrosea", user: str = "test_user", bits: int = 100):

    EVENT_QUEUE.append({
        "type": "channel.cheer",
        "event": {
            "broadcaster_user_login": channel,
            "user_name": user,
            "bits": bits
        }
    })

    return {"queued": "cheer event"}


# =========================
# 🔴 STREAM START
# =========================
@router.get("/live")
async def test_live(channel: str = "itsfrosea"):

    EVENT_QUEUE.append({
        "type": "stream.online",
        "event": {
            "broadcaster_user_login": channel
        }
    })

    return {"queued": "stream online"}


# =========================
# ⚫ STREAM END
# =========================
@router.get("/offline")
async def test_offline(channel: str = "itsfrosea"):

    EVENT_QUEUE.append({
        "type": "stream.offline",
        "event": {
            "broadcaster_user_login": channel
        }
    })

    return {"queued": "stream offline"}


# =========================
# 🚀 TEST EVERYTHING
# =========================
@router.get("/all")
async def test_all(channel: str = "itsfrosea"):

    EVENT_QUEUE.append({
        "type": "stream.online",
        "event": {"broadcaster_user_login": channel}
    })

    EVENT_QUEUE.append({
        "type": "channel.follow",
        "event": {
            "broadcaster_user_login": channel,
            "user_name": "test_follow"
        }
    })

    EVENT_QUEUE.append({
        "type": "channel.subscribe",
        "event": {
            "broadcaster_user_login": channel,
            "user_name": "test_sub",
            "tier": "1"
        }
    })

    EVENT_QUEUE.append({
        "type": "channel.cheer",
        "event": {
            "broadcaster_user_login": channel,
            "user_name": "test_cheer",
            "bits": 100
        }
    })

    return {"queued": "all events"}