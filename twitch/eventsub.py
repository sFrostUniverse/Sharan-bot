import os
import hmac
import hashlib
import json
from pathlib import Path

from fastapi import APIRouter, Request, Header, HTTPException, Response
from dotenv import load_dotenv

from event_queue import EVENT_QUEUE

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
    twitch_eventsub_message_id: str = Header(None, alias="Twitch-Eventsub-Message-Id"),
    twitch_eventsub_message_timestamp: str = Header(None, alias="Twitch-Eventsub-Message-Timestamp"),
    twitch_eventsub_message_signature: str = Header(None, alias="Twitch-Eventsub-Message-Signature"),
    twitch_eventsub_message_type: str = Header(None, alias="Twitch-Eventsub-Message-Type"),
):
    raw_body = await request.body()

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    print("📩 EventSub type:", twitch_eventsub_message_type)

    # 1️⃣ VERIFICATION CHALLENGE
    if twitch_eventsub_message_type == "webhook_callback_verification":
        print("✅ EventSub verification received")
        return Response(
            content=payload["challenge"],
            media_type="text/plain",
            status_code=200
        )

    # 2️⃣ SIGNATURE VERIFICATION
    if not verify_signature(
        twitch_eventsub_message_id,
        twitch_eventsub_message_timestamp,
        raw_body,
        twitch_eventsub_message_signature,
    ):
        print("❌ Invalid EventSub signature")
        raise HTTPException(status_code=403, detail="Invalid EventSub signature")

    # 3️⃣ NOTIFICATION ONLY
    if twitch_eventsub_message_type != "notification":
        return Response(status_code=204)

    event_type = payload["subscription"]["type"]
    event = payload.get("event", {})

    print("📦 QUEUED EVENT:", event_type)

    # ✅ STORE EVENT (NO SIDE EFFECTS)
    EVENT_QUEUE.append({
        "type": event_type,
        "event": event,
    })

    return Response(status_code=204)