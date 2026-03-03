import os
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
REDIRECT_URI = "https://sharan-bot-kp71.onrender.com/auth/twitch/callback"

SCOPES = "chat:read chat:edit channel:read:subscriptions"


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