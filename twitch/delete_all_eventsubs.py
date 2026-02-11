import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

# get app token
token = requests.post(
    "https://id.twitch.tv/oauth2/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    },
).json()["access_token"]

headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {token}",
}

# list subs
subs = requests.get(
    "https://api.twitch.tv/helix/eventsub/subscriptions",
    headers=headers,
).json()["data"]

for sub in subs:
    sid = sub["id"]
    r = requests.delete(
        f"https://api.twitch.tv/helix/eventsub/subscriptions?id={sid}",
        headers=headers,
    )
    print("Deleted:", sub["type"], r.status_code)
