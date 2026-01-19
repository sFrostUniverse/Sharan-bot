import os
import asyncio
import random

AUTO_MESSAGE_INTERVAL = 15 * 60  # 15 minutes

FOLLOW_MESSAGES = [
    "💜 Hey cuties~ if you’re enjoying the vibes, tap that FOLLOW button for me 😘",
    "✨ New here? Don’t be shy~ hit FOLLOW and stay with me 💕",
    "👀 Watching silently? I see you~ follow me already 😏💜",
    "💖 If I made you smile even once, you owe me a FOLLOW 😌",
    "🌸 Stick around, babes~ following helps me more than you know 💕",
]

COMMAND_MESSAGES = [
    "🎮 Wanna cause chaos? Try !kill @username 😈",
    "😂 Need a laugh? Type !joke and tag me with your answer~",
    "💥 Chat games are ON~ try !kill or !joke 💜",
    "👀 Bored? Wake chat up with !kill or !joke 😘",
    "😈 Feeling playful? !joke always hits~",
]





class AdsManager:
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self._task: asyncio.Task | None = None
        self._send_follow_next = True  # 🔁 alternator

    def start(self):
        if self._task is None:
            self._task = self.bot.loop.create_task(self._loop())

    async def _loop(self):
        while True:
            await asyncio.sleep(AUTO_MESSAGE_INTERVAL)

            if not self.enabled:
                continue

            channel = self.bot.get_channel(
                os.getenv("TWITCH_CHAT_CHANNEL")
            )
            if not channel:
                continue

            if self._send_follow_next:
                message = random.choice(FOLLOW_MESSAGES)
            else:
                message = random.choice(COMMAND_MESSAGES)

            self._send_follow_next = not self._send_follow_next  # 🔁 flip
            await channel.send(message)

    # ===== controls =====
    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def status(self) -> bool:
        return self.enabled

