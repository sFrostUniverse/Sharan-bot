from twitch.api import get_stream_info
import os

# --- THANK YOU MESSAGES (unchanged) ---

async def follow_message(username):
    return f"💜 Thank you for the follow, @{username}! Welcome to the stream ✨"

async def sub_message(username, tier="1"):
    return f"🌟 THANK YOU @{username} for subscribing! Enjoy the art vibes 💜"

async def cheer_message(username, bits):
    return f"💎 @{username} just cheered {bits} bits! Thank you so much 💜✨"


# --- STREAM START MESSAGE (dynamic) ---

from twitch.api import get_stream_info
import os

async def stream_start_message():
    channel = os.getenv("TWITCH_CHAT_CHANNEL")
    info = get_stream_info(channel)

    # NOT LIVE
    if not info:
        return "💤 The stream is currently offline, but we’ll be live soon 💜"

    # LIVE
    title = info["title"]
    game = info["game"]

    return (
        f"🔴 The stream is now LIVE!\n"
        f"🎨 {game}\n"
        f"📌 {title} 💜"
    )

