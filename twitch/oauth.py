import os
import aiohttp
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# =========================
# 🔐 ENV
# =========================
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

REDIRECT_URI = "https://sharan-bot-kp71.onrender.com/auth/twitch/callback"

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

        # 1️⃣ Exchange code for access token
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

        return {
            "success": True,
            "login": user["login"],
            "display_name": user["display_name"],
            "broadcaster_id": user["id"],
        }