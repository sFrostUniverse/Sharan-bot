import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")
BROADCASTER_ID = os.getenv("TWITCH_BROADCASTER_ID")

CALLBACK_URL = "https://sharan-bot-kp71.onrender.com/eventsub"

# =========================
# VALIDATION
# =========================
assert CLIENT_ID, "Missing TWITCH_CLIENT_ID"
assert CLIENT_SECRET, "Missing TWITCH_CLIENT_SECRET"
assert EVENTSUB_SECRET, "Missing TWITCH_EVENTSUB_SECRET"
assert BROADCASTER_ID, "Missing TWITCH_BROADCASTER_ID"

print("✅ Environment OK")

# =========================
# GET APP TOKEN
# =========================
token_resp = requests.post(
    "https://id.twitch.tv/oauth2/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
)

token_data = token_resp.json()
ACCESS_TOKEN = token_data["access_token"]

print("✅ App access token obtained")

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# =========================
# SUBSCRIPTIONS
# =========================

SUBSCRIPTIONS = [
    # 🔴 STREAM ONLINE
    {
        "type": "stream.online",
        "version": "1",
        "condition": {"broadcaster_user_id": BROADCASTER_ID},
    },
    # ⚫ STREAM OFFLINE
    {
        "type": "stream.offline",
        "version": "1",
        "condition": {"broadcaster_user_id": BROADCASTER_ID},
    },
    # 💜 FOLLOW (v2, requires moderator)
    {
        "type": "channel.follow",
        "version": "2",
        "condition": {
            "broadcaster_user_id": BROADCASTER_ID,
            "moderator_user_id": BROADCASTER_ID,
        },
    },
    # 🌟 SUBSCRIBE
    {
        "type": "channel.subscribe",
        "version": "1",
        "condition": {"broadcaster_user_id": BROADCASTER_ID},
    },
    # 🎁 SUB GIFT (optional but recommended)
    {
        "type": "channel.subscription.gift",
        "version": "1",
        "condition": {"broadcaster_user_id": BROADCASTER_ID},
    },
]

# =========================
# CREATE SUBSCRIPTIONS
# =========================
for sub in SUBSCRIPTIONS:
    payload = {
        **sub,
        "transport": {
            "method": "webhook",
            "callback": CALLBACK_URL,
            "secret": EVENTSUB_SECRET,
        },
    }

    resp = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers=HEADERS,
        json=payload,
    )

    print(f"{sub['type']} → {resp.status_code}")
    print(resp.json())
