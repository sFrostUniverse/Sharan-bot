import os
import time
import aiohttp
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
    raise RuntimeError("TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET is not set")

_token: str | None = None
_token_expiry: float = 0.0


# =========================
# 🔑 APP ACCESS TOKEN
# =========================

async def get_app_token() -> str:
    """
    Fetch (or reuse) Twitch App Access Token.
    Uses async HTTP to avoid blocking the event loop.
    """
    global _token, _token_expiry

    if _token and time.time() < _token_expiry:
        return _token

    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            data = await resp.json()

    if "access_token" not in data:
        raise RuntimeError(f"Failed to obtain Twitch token: {data}")

    _token = data["access_token"]
    _token_expiry = time.time() + data["expires_in"] - 60

    print("🟣 Twitch app token refreshed")

    return _token


# =========================
# 📡 STREAM INFO
# =========================
async def get_user_id(login: str) -> str | None:
    token = await get_app_token()
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.twitch.tv/helix/users",
            headers=headers,
            params={"login": login},
        ) as resp:
            data = await resp.json()

    users = data.get("data", [])
    if not users:
        return None

    return users[0]["id"]

async def get_stream_info(broadcaster_login: str) -> dict | None:
    """
    Returns stream title & game if LIVE, else None.
    Fully async, non-blocking.
    """
    token = await get_app_token()

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }

    async with aiohttp.ClientSession() as session:
        # 1️⃣ Get user ID
        async with session.get(
            "https://api.twitch.tv/helix/users",
            headers=headers,
            params={"login": broadcaster_login},
        ) as user_resp:
            user_json = await user_resp.json()

        user_data = user_json.get("data", [])
        if not user_data:
            return None

        user_id = user_data[0]["id"]

        # 2️⃣ Get stream info
        async with session.get(
            "https://api.twitch.tv/helix/streams",
            headers=headers,
            params={"user_id": user_id},
        ) as stream_resp:
            stream_json = await stream_resp.json()

    stream_data = stream_json.get("data", [])
    if not stream_data:
        return None

    stream = stream_data[0]

    return {
        "title": stream.get("title", "Untitled Stream"),
        "game": stream.get("game_name", "Just Chatting"),
    }
