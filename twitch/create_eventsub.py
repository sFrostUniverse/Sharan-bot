import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# =========================
# LOAD .env FROM PROJECT ROOT
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# =========================
# ENV VARIABLES
# =========================
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")

# Your Twitch broadcaster ID
BROADCASTER_ID = os.getenv("TWITCH_BROADCASTER_ID")


# Your public webhook endpoint
CALLBACK_URL = "https://sharan-bot-kp71.onrender.com/eventsub"

# =========================
# VALIDATION
# =========================
if not CLIENT_ID:
    raise RuntimeError("TWITCH_CLIENT_ID missing in .env")

if not CLIENT_SECRET:
    raise RuntimeError("TWITCH_CLIENT_SECRET missing in .env")

if not EVENTSUB_SECRET:
    raise RuntimeError("TWITCH_EVENTSUB_SECRET missing in .env")

print("✅ Environment variables loaded")

# =========================
# 1️⃣ GET APP ACCESS TOKEN
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

if "access_token" not in token_data:
    raise RuntimeError(f"Failed to get token: {token_data}")

ACCESS_TOKEN = token_data["access_token"]
print("✅ App access token obtained")

# =========================
# 2️⃣ CREATE EVENTSUB (stream.online)
# =========================
payload = {
    "type": "stream.online",
    "version": "1",
    "condition": {
        "broadcaster_user_id": BROADCASTER_ID
    },
    "transport": {
        "method": "webhook",
        "callback": CALLBACK_URL,
        "secret": EVENTSUB_SECRET
    }
}
payload_offline = {
    "type": "stream.offline",
    "version": "1",
    "condition": {
        "broadcaster_user_id": BROADCASTER_ID
    },
    "transport": {
        "method": "webhook",
        "callback": CALLBACK_URL,
        "secret": EVENTSUB_SECRET
    }
}


resp = requests.post(
    "https://api.twitch.tv/helix/eventsub/subscriptions",
    headers={
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    },
    json=payload,
)

print("STATUS:", resp.status_code)
print(resp.json())

resp2 = requests.post(
    "https://api.twitch.tv/helix/eventsub/subscriptions",
    headers={
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    },
    json=payload_offline,
)

print("OFFLINE STATUS:", resp2.status_code)
print(resp2.json())

