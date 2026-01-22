import os
import hmac
import hashlib
import asyncio
from pathlib import Path

from fastapi import APIRouter, Request, Header, HTTPException, Response
from dotenv import load_dotenv

from twitch.greetings import (
    follow_message,
    sub_message,
    cheer_message,
    stream_start_message,
)

# ─────────────────────────────
# ENV
# ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")
if not EVENTSUB_SECRET:
    raise RuntimeError("TWITCH_EVENTSUB_SECRET missing")

router = APIRouter()

# ─────────────────────────────
# SIGNATURE VERIFY
# ─────────────────────────────
def verify_signature(message_id: str, timestamp: str, body: bytes, signature: str) -> bool:
    if not message_id or not timestamp or not signature:
        return False

    message = message_id.encode() + timestamp.encode() + body
    expected = "sha256=" + hmac.new(
        EVENTSUB_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

# ─────────────────────────────
# EVENTSUB WEBHOOK
# ─────────────────────────────
@router.post("/eventsub")
async def eventsub_handler(
    request: Request,
    twitch_eventsub_message_id: str = Header(None),
    twitch_eventsub_message_timestamp: str = Header(None),
    twitch_eventsub_message_signature: str = Header(None),
):
    body = await request.body()
    payload = await request.json()

    print("📩 EVENTSUB HIT")

    # ✅ 1. HANDLE CHALLENGE FIRST (NO SIGNATURE CHECK)
    if payload.get("challenge"):
        print("✅ EVENTSUB VERIFIED")
        return Response(
            content=payload["challenge"],
            media_type="text/plain",
            status_code=200
        )

    # ✅ 2. VERIFY SIGNATURE FOR REAL EVENTS
    if not verify_signature(
        twitch_eventsub_message_id,
        twitch_eventsub_message_timestamp,
        body,
        twitch_eventsub_message_signature,
    ):
        raise HTTPException(status_code=403, detail="Invalid EventSub signature")

    event_type = payload["subscription"]["type"]
    event = payload.get("event", {})

    # 🔁 Import late (avoid circular / startup issues)
    from twitch.twitch_chat import send_chat_message

    # ─────────────────────────────
    # EVENT HANDLING (NON-BLOCKING)
    # ─────────────────────────────

    if event_type == "stream.online":
        asyncio.create_task(send_chat_message(await stream_start_message()))

    elif event_type == "stream.offline":
        asyncio.create_task(send_chat_message("_STREAM_OFF_"))

    elif event_type == "channel.follow":
        asyncio.create_task(
            send_chat_message(follow_message(event["user_name"]))
        )

    elif event_type == "channel.subscribe":
        username = event["user_name"]
        months = event.get("cumulative_months", 1)
        tier = event.get("tier", "1")

        if months > 1:
            msg = f"💜 Welcome back @{username}! Thanks for resubbing ✨"
        else:
            msg = sub_message(username, tier)

        asyncio.create_task(send_chat_message(msg))

    elif event_type == "channel.cheer":
        asyncio.create_task(
            send_chat_message(
                cheer_message(event["user_name"], event["bits"])
            )
        )

    print("📦 EVENT:", event_type)
    return Response(status_code=204)
