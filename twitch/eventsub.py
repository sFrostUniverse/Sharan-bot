import os
import hmac
import hashlib
from fastapi import FastAPI, Request, Header, HTTPException
from twitch.greetings import follow_message, sub_message, cheer_message
from twitch.twitch_chat import send_chat_message

app = FastAPI()

EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")

def verify_signature(message_id, timestamp, body, signature):
    msg = message_id + timestamp + body
    expected = "sha256=" + hmac.new(
        EVENTSUB_SECRET.encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/eventsub")
async def eventsub_handler(
    request: Request,
    twitch_eventsub_message_id: str = Header(None),
    twitch_eventsub_message_timestamp: str = Header(None),
    twitch_eventsub_message_signature: str = Header(None),
):
    body = await request.body()
    body_str = body.decode()

    if not verify_signature(
        twitch_eventsub_message_id,
        twitch_eventsub_message_timestamp,
        body_str,
        twitch_eventsub_message_signature,
    ):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # 🔐 Verification handshake
    if payload["subscription"]["type"] == "channel.follow":
        if payload.get("challenge"):
            return payload["challenge"]

    event_type = payload["subscription"]["type"]
    event = payload["event"]

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
