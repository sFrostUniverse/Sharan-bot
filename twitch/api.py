import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()  # 🔥 THIS WAS MISSING

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

_token = None
_token_expiry = 0


def get_app_token():
    global _token, _token_expiry

    if _token and time.time() < _token_expiry:
        return _token

    url = "https://id.twitch.tv/oauth2/token"

    payload = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    resp = requests.post(url, data=payload)
    data = resp.json()

    # 🔎 DEBUG (temporary, but VERY useful)
    print("TWITCH OAUTH RESPONSE:", data)

    if "access_token" not in data:
        raise RuntimeError("Failed to obtain Twitch app access token")

    _token = data["access_token"]
    _token_expiry = time.time() + data["expires_in"] - 60
    return _token


def get_stream_info(broadcaster_login: str):
    token = get_app_token()
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    # 1️⃣ Get user ID
    user_resp = requests.get(
        "https://api.twitch.tv/helix/users",
        headers=headers,
        params={"login": broadcaster_login}
    )
    user_data = user_resp.json()["data"]
    if not user_data:
        return None

    user_id = user_data[0]["id"]

    # 2️⃣ Get stream info
    stream_resp = requests.get(
        "https://api.twitch.tv/helix/streams",
        headers=headers,
        params={"user_id": user_id}
    )
    stream_data = stream_resp.json()["data"]

    if not stream_data:
        return None

    return {
        "title": stream_data[0]["title"],
        "game": stream_data[0]["game_name"]
    }
