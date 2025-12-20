import os
from dotenv import load_dotenv
from twitchio.ext import commands

from twitch.greetings import stream_start_message

load_dotenv()

twitch_bot_instance: "SharanTwitchBot | None" = None


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

    async def start_bot(self):
        print("🟣 Starting Twitch chat bot...")
        await super().start()

    # =========================
    # 🎮 EVENTS (MUST BE INSIDE CLASS)
    # =========================

    async def event_ready(self):
        global twitch_bot_instance
        twitch_bot_instance = self

        print("🟣 Twitch chat connected")
        print(f"Logged in as: {self.nick}")
        print("TWITCH_CHAT_CHANNEL =", repr(os.getenv("TWITCH_CHAT_CHANNEL")))

    async def event_message(self, message):
        if message.echo:
            return

        print(
            f"[TWITCH MESSAGE] "
            f"user={message.author.name} "
            f"content={repr(message.content)}"
        )

        content = message.content.lower().strip()

        if content in {"hello", "!hello"}:
            await message.channel.send(
                f"Hello @{message.author.name} 💜 I am Sharan!"
            )

        elif content == "!discord":
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
    if not twitch_bot_instance:
        print("⚠️ Twitch bot not ready yet")
        return

    channel_name = os.getenv("TWITCH_CHAT_CHANNEL")
    channel = twitch_bot_instance.get_channel(channel_name)

    if not channel:
        print(f"⚠️ Twitch channel not found: {channel_name}")
        return

    await channel.send(text)
