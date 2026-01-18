# twitch/jokes.py

import os
import asyncio
import aiohttp
import random

JOKE_INTERVAL = 3 * 60  # 3 minutes
PUNCHLINE_DELAY_RANGE = (2, 4)  # seconds


class JokeManager:
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False
        self._task: asyncio.Task | None = None

    def start(self):
        if self._task is None:
            self._task = self.bot.loop.create_task(self._loop())

    async def _loop(self):
        while True:
            await asyncio.sleep(JOKE_INTERVAL)

            if not self.enabled:
                continue

            channel = self.bot.get_channel(
                os.getenv("TWITCH_CHAT_CHANNEL")
            )
            if not channel:
                continue

            joke = await self._fetch_joke()
            if not joke:
                continue

            setup, punchline = joke

            # 1️⃣ send setup
            await channel.send(f"😂 {setup}")

            # 2️⃣ wait a bit (natural timing)
            delay = random.uniform(*PUNCHLINE_DELAY_RANGE)
            await asyncio.sleep(delay)

            # 3️⃣ send punchline
            await channel.send(f"👉 {punchline}")

    async def _fetch_joke(self) -> tuple[str, str] | None:
        url = "https://official-joke-api.appspot.com/jokes/random"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    data = await resp.json()

            setup = data.get("setup")
            punchline = data.get("punchline")

            if setup and punchline:
                return setup, punchline

        except Exception as e:
            print("❌ Joke fetch failed:", e)

        return None

    # ===== controls =====
    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def status(self) -> bool:
        return self.enabled
