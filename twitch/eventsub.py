import os
import hmac
import hashlib
from pathlib import Path
from fastapi import APIRouter, Request, Header, HTTPException
from dotenv import load_dotenv
from twitch.medals import reset_medals, end_stream

from twitch.greetings import (
    follow_message,
    sub_message,
    cheer_message,
    stream_start_message,
)

# =========================
# LOAD ENV (IMPORTANT)
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

router = APIRouter()

EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")
if not EVENTSUB_SECRET:
    raise RuntimeError("TWITCH_EVENTSUB_SECRET is not set")

# =========================
# SIGNATURE VERIFICATION
# =========================

def verify_signature(message_id: str, timestamp: str, body: bytes, signature: str) -> bool:
    message = message_id.encode() + timestamp.encode() + body
    expected = "sha256=" + hmac.new(
        EVENTSUB_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# =========================
# EVENTSUB ENDPOINT
# =========================

@router.post("/eventsub")
async def eventsub_handler(
    request: Request,
    twitch_eventsub_message_id: str = Header(...),
    twitch_eventsub_message_timestamp: str = Header(...),
    twitch_eventsub_message_signature: str = Header(...),
):
    body = await request.body()

    if not verify_signature(
        twitch_eventsub_message_id,
        twitch_eventsub_message_timestamp,
        body,
        twitch_eventsub_message_signature,
    ):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # 🔑 Verification handshake
    if payload.get("challenge"):
        return payload["challenge"]

    event_type = payload["subscription"]["type"]
    event = payload.get("event", {})

    # 🔁 SAFE late import (queue-based)
    from twitch.twitch_chat import send_chat_message

    # =========================
    # EVENT HANDLING
    # =========================

    from twitch.medals import reset_medals, end_stream, set_stream_active

    if event_type == "stream.online":
        reset_medals()
        set_stream_active(True)
        await send_chat_message(await stream_start_message())

    elif event_type == "stream.offline":
        set_stream_active(False)
        end_stream()

    if event_type == "stream.online":
        await send_chat_message("_STREAM_ON_")
        await send_chat_message(await stream_start_message())

    elif event_type == "stream.offline":
        await send_chat_message("_STREAM_OFF_")


    elif event_type == "channel.follow":
        await send_chat_message(follow_message(event["user_name"]))

    elif event_type == "channel.subscribe":
        username = event["user_name"]
        months = event.get("cumulative_months", 1)
        tier = event.get("tier", "1")

        if months > 1:
            msg = f"💜 Welcome back @{username}! Thanks for resubbing ✨"
        else:
            msg = sub_message(username, tier)

        await send_chat_message(msg)

    elif event_type == "channel.cheer":
        await send_chat_message(
            cheer_message(event["user_name"], event["bits"])
        )

    return {"status": "ok"}
