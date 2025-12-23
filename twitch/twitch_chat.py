import os
import time
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands


from twitch.greetings import stream_start_message

load_dotenv()

twitch_bot_instance: "SharanTwitchBot | None" = None
twitch_ready = False


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

        # cooldown memory for polite replies
        self.last_service_reply = {}

    async def start_bot(self):
        print("🟣 Starting Twitch chat bot...")
        await super().start()

    # =========================
    # 🎮 EVENTS
    # =========================

    async def event_ready(self):
        global twitch_bot_instance, twitch_ready
        twitch_bot_instance = self
        twitch_ready = True

        print("🟣 Twitch chat connected")
        print(f"Logged in as: {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return

        content = message.content.lower().strip()

        print(
            f"[TWITCH MESSAGE] "
            f"user={message.author.name} "
            f"content={repr(message.content)}"
        )

        # Ignore mods & broadcaster
        if message.author.is_mod or message.author.is_broadcaster:
            await self.handle_commands(message)
            return

        # =========================
        # 🚫 POLITE PROMO / SERVICE REPLY
        # =========================
        if any(keyword in content for keyword in SERVICE_KEYWORDS):
            now = time.time()
            last = self.last_service_reply.get(message.author.name, 0)

            # reply only once every 10 minutes per user
            if now - last > 600:
                await message.channel.send(
                    f"💜 Hey @{message.author.name}, we don’t allow promotions or service offers here. "
                    f"Feel free to enjoy the stream and chat with us ✨"
                )
                self.last_service_reply[message.author.name] = now

            return  # stop further processing

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

        # 🔑 REQUIRED FOR COMMAND PROCESSING
        await self.handle_commands(message)


# =========================
# 📤 EXTERNAL SEND HELPER
# =========================

    async def send_chat_message(text: str):
        global twitch_ready

        # wait up to 10 seconds for Twitch chat to be ready
        for _ in range(20):
            if twitch_ready:
                break
            await asyncio.sleep(0.5)

        if not twitch_ready or not twitch_bot_instance:
            print("⚠️ Twitch bot not ready, dropping auto message")
            return

        channel_name = os.getenv("TWITCH_CHAT_CHANNEL")
        channel = twitch_bot_instance.get_channel(channel_name)

        if not channel:
            print(f"⚠️ Twitch channel not found: {channel_name}")
            return

        await channel.send(text)

