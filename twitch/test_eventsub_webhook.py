import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET")

# =========================
# GET APP ACCESS TOKEN
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

print("✅ App token obtained")

# =========================
# LIST EVENTSUB SUBSCRIPTIONS
# =========================
resp = requests.get(
    "https://api.twitch.tv/helix/eventsub/subscriptions",
    headers={
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    },
)

data = resp.json()

print("\n📡 EVENTSUB SUBSCRIPTIONS:\n")

for sub in data.get("data", []):
    print(f"- Type: {sub['type']}")
    print(f"  Status: {sub['status']}")
    print(f"  ID: {sub['id']}")
    print("-" * 30)

print(f"\nTotal subscriptions: {data.get('total', 0)}")
