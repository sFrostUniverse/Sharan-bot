import os
import aiohttp
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

from event_queue import EVENT_QUEUE

load_dotenv()

router = APIRouter()

# =========================
# 🔐 ENV
# =========================
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")

REDIRECT_URI = "https://sharan-bot-kp71.onrender.com/auth/twitch/callback"
CALLBACK_URL = "https://sharan-bot-kp71.onrender.com/eventsub"

SCOPES = "chat:read chat:edit channel:read:subscriptions"

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET missing")


# =========================
# 🔹 LOGIN ROUTE
# =========================
@router.get("/auth/twitch/login")
async def twitch_login():
    url = (
        "https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        f"&scope={SCOPES}"
    )
    return RedirectResponse(url)


# =========================
# 🔹 CALLBACK ROUTE
# =========================
@router.get("/auth/twitch/callback")
async def twitch_callback(code: str):

    async with aiohttp.ClientSession() as session:

        # 1️⃣ Exchange user code
        token_resp = await session.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
            },
        )

        token_data = await token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail=token_data)

        # 2️⃣ Get user info
        user_resp = await session.get(
            "https://api.twitch.tv/helix/users",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": CLIENT_ID,
            },
        )

        user_data = await user_resp.json()

        if "data" not in user_data or not user_data["data"]:
            raise HTTPException(status_code=400, detail=user_data)

        user = user_data["data"][0]
        login = user["login"]
        broadcaster_id = user["id"]

        print(f"✅ OAuth success for {login}")

        # 3️⃣ Get APP access token (for EventSub)
        app_token_resp = await session.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        )

        app_token_data = await app_token_resp.json()
        app_access_token = app_token_data.get("access_token")

        if not app_access_token:
            raise HTTPException(status_code=400, detail=app_token_data)

        headers = {
            "Authorization": f"Bearer {app_access_token}",
            "Client-Id": CLIENT_ID,
            "Content-Type": "application/json",
        }

        # 4️⃣ Create EventSub subscriptions
        event_types = [
            "stream.online",
            "stream.offline",
            "channel.follow",
            "channel.subscribe",
            "channel.cheer",
        ]

        for event_type in event_types:
            await session.post(
                "https://api.twitch.tv/helix/eventsub/subscriptions",
                headers=headers,
                json={
                    "type": event_type,
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": broadcaster_id
                    },
                    "transport": {
                        "method": "webhook",
                        "callback": CALLBACK_URL,
                        "secret": EVENTSUB_SECRET,
                    },
                },
            )

        print(f"🎯 EventSub created for {login}")

        # 5️⃣ Push to Sparked via queue
        EVENT_QUEUE.append({
            "type": "channel.added",
            "event": {
                "login": login,
                "broadcaster_user_login": login
            }
        })

        print(f"🚀 Queued onboarding for {login}")

        return {
            "success": True,
            "onboarded_channel": login
        }