import os
import asyncio
import time
from dotenv import load_dotenv
from twitchio.ext import commands
from twitch.greetings import stream_start_message
from twitch.games import handle_kill


load_dotenv()

# =========================
# 🌐 GLOBAL BOT STATE
# =========================
twitch_bot_instance: "SharanTwitchBot | None" = None

# 🔁 ASYNC MESSAGE QUEUE (CRITICAL FIX)
message_queue: asyncio.Queue[str] = asyncio.Queue()

# =========================
# 🚫 SERVICE / PROMO FILTER
# =========================
SERVICE_KEYWORDS = [
    "service",
    "services",
    "designer",
    "editor",
    "promotion",
    "promote",
    "dm me",
    "hire me",
    "freelance",
    "work with you",
    "discord.gg",
    "join my discord",
    "check my discord",
]


class SharanTwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("TWITCH_TOKEN"),
            client_id=os.getenv("TWITCH_CLIENT_ID"),
            client_secret=os.getenv("TWITCH_CLIENT_SECRET"),
            bot_id=os.getenv("TWITCH_BOT_ID"),
            prefix="!",
            initial_channels=[os.getenv("TWITCH_CHAT_CHANNEL")],
        )

        self.last_service_reply = {}

    async def start_bot(self):
        print("🟣 Starting Twitch chat bot...")
        await super().start()

    # =========================
    # 🎮 EVENTS
    # =========================
    async def event_ready(self):
        global twitch_bot_instance
        twitch_bot_instance = self

        # start message sender loop
        self.loop.create_task(self._message_sender())

        print("🟣 Twitch chat connected")
        print(f"Logged in as: {self.nick}")

        # 🔴 AUTO LIVE MESSAGE (SAME AS !live)
        msg = await stream_start_message()
        if "LIVE" in msg:
            await send_chat_message(msg)


    async def event_message(self, message):
        if message.echo:
            return

        content = message.content.lower().strip()

        print(
            f"[TWITCH MESSAGE] "
            f"user={message.author.name} "
            f"content={repr(message.content)}"
        )
        # =========================
        # 🎮 CHAT GAMES
        # =========================
        handled = await handle_kill(message, message.content)
        if handled:
            return


        # Ignore mods & broadcaster for promo filter
        if not (message.author.is_mod or message.author.is_broadcaster):
            if any(keyword in content for keyword in SERVICE_KEYWORDS):
                now = time.time()
                last = self.last_service_reply.get(message.author.name, 0)

                if now - last > 600:
                    await message.channel.send(
                        f"💜 Hey @{message.author.name}, we don’t allow promotions here. "
                        f"Enjoy the stream ✨"
                    )
                    self.last_service_reply[message.author.name] = now

                return

        # =========================
        # 🎯 BASIC COMMANDS
        # =========================
        if content == "!discord":
            await message.channel.send(
                "💜 Join our Discord here: https://discord.gg/33Gsen7xhY"
            )

        elif content == "!live":
            msg = await stream_start_message()
            await message.channel.send(msg)

        await self.handle_commands(message)

    # =========================
    # 🔁 MESSAGE SENDER LOOP
    # =========================

    async def _message_sender(self):
        while True:
            msg = await message_queue.get()

            channel = self.get_channel(os.getenv("TWITCH_CHAT_CHANNEL"))
            if channel:
                await channel.send(msg)


# =========================
# 📤 SAFE EXTERNAL SEND (USED BY EVENTSUB)
# =========================

async def send_chat_message(text: str):
    await message_queue.put(text)
