import os
from twitch.api import get_stream_info
import asyncio

# =========================
# 💜 THANK YOU MESSAGES
# =========================

def follow_message(username: str) -> str:
    return f"💜 Thank you for the follow, @{username}! Welcome to the stream ✨"


def sub_message(username: str, tier: str = "1") -> str:
    return f"🌟 THANK YOU @{username} for subscribing! Enjoy the art vibes 💜"


def cheer_message(username: str, bits: int) -> str:
    return f"💎 @{username} just cheered {bits} bits! Thank you so much 💜✨"


# =========================
# 🔴 STREAM START MESSAGE
# =========================

async def stream_start_message() -> str:
    channel = os.getenv("TWITCH_CHAT_CHANNEL")

    if not channel:
        return "⚠️ Twitch channel not configured."

    info = None
    for _ in range(5):  # retry up to ~10 seconds
        info = await get_stream_info(channel)
        if info:
            break
        await asyncio.sleep(2)

    if not info:
        return "🔴 We’re LIVE! Hop in 💜"

    title = info.get("title", "Untitled Stream")
    game = info.get("game") or info.get("game_name") or "Just Chatting"

    return (
        f"🔴 The stream is now LIVE!\n"
        f"🎮 {game}\n"
        f"📌 {title} 💜"
    )
