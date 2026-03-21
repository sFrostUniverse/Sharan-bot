import asyncio
import os
import aiohttp

from twitch.twitch_chat import send_chat_message
from twitch.medals import reset_medals
from twitch.points import add_points
from twitch.greetings import (
    follow_message,
    sub_message,
    cheer_message,
    stream_start_message,
)

RENDER_EVENTS_URL = os.getenv("RENDER_EVENTS_URL")
INTERNAL_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")


async def poll_render_events():
    print("🔁 Render EventSub poller started (aiohttp)")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    RENDER_EVENTS_URL,
                    headers={"X-Internal-Secret": INTERNAL_SECRET},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        events = await resp.json()
                        for item in events:
                            await handle_event(item)

            except Exception as e:
                print("⚠️ Render poll error:", e)

            await asyncio.sleep(5)


async def handle_event(item: dict):
    event_type = item["type"]
    event = item["event"]

    if event_type == "stream.online":
        reset_medals()
        await send_chat_message(await stream_start_message())

    elif event_type == "stream.offline":
        await send_chat_message("_STREAM_OFF_")

    elif event_type == "channel.follow":
        user = event["user_name"]
        add_points(user, 50)
        await send_chat_message(follow_message(user))

    elif event_type == "channel.subscribe":
        user = event["user_name"]
        await send_chat_message(sub_message(user, event.get("tier", "1")))

    elif event_type == "channel.cheer":
        await send_chat_message(
            cheer_message(event["user_name"], event["bits"])
        )