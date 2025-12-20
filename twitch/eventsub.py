import os
import hmac
import hashlib
from fastapi import FastAPI, Request, Header, HTTPException
from twitch.greetings import follow_message, sub_message, cheer_message
from twitch.twitch_chat import send_chat_message

app = FastAPI()

EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")

if not EVENTSUB_SECRET:
    raise RuntimeError("TWITCH_EVENTSUB_SECRET is not set")


# =========================
# 🔐 SIGNATURE VERIFICATION
# =========================

def verify_signature(
    message_id: str,
    timestamp: str,
    body: bytes,
    signature: str,
) -> bool:
    """
    Twitch EventSub signature verification.
    Must use RAW BODY BYTES.
    """
    message = message_id.encode() + timestamp.encode() + body

    expected_signature = "sha256=" + hmac.new(
        EVENTSUB_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


# =========================
# 📡 EVENTSUB HANDLER
# =========================

@app.post("/eventsub")
async def eventsub_handler(
    request: Request,
    twitch_eventsub_message_id: str = Header(...),
    twitch_eventsub_message_timestamp: str = Header(...),
    twitch_eventsub_message_signature: str = Header(...),
):
    body = await request.body()

    # 🔐 Verify Twitch signature FIRST
    if not verify_signature(
        twitch_eventsub_message_id,
        twitch_eventsub_message_timestamp,
        body,
        twitch_eventsub_message_signature,
    ):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # =========================
    # 🔑 VERIFICATION HANDSHAKE
    # =========================
    if payload.get("challenge"):
        return payload["challenge"]

    event_type = payload["subscription"]["type"]
    event = payload.get("event", {})

    # =========================
    # 🎯 EVENT HANDLING
    # =========================

    if event_type == "channel.follow":
        msg = await follow_message(event["user_name"])
        await send_chat_message(msg)

    elif event_type == "channel.subscribe":
        msg = await sub_message(event["user_name"])
        await send_chat_message(msg)

    elif event_type == "channel.cheer":
        msg = await cheer_message(event["user_name"], event["bits"])
        await send_chat_message(msg)

    return {"status": "ok"}
