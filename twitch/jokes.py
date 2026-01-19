# twitch/jokes.py

import os
import asyncio
import aiohttp
import random

ANSWER_TIMEOUT = 13  # seconds
PUNCHLINE_DELAY_RANGE = (2, 4)

# =========================
# 😈 LIFE SARCASM WRAPPERS
# =========================

SARCASM_PREFIX = [
    "😐 Okay chat… don’t take this personally.",
    "🫠 Life really said:",
    "😮‍💨 This one feels unnecessary, but okay.",
    "🖤 I didn’t ask for this reminder, yet here we are.",
]

SARCASM_SUFFIX = [
    "Yeah… that tracks.",
    "Anyway, I’m fine. Totally.",
    "Life is beautiful. Allegedly.",
    "That joke hurt a little.",
    "Why is this so accurate though?",
]

# =========================
# 😂 JOKE MANAGER
# =========================

class JokeManager:
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.current_punchline: str | None = None
        self._answer_event = asyncio.Event()

    # =========================
    # PUBLIC API
    # =========================

    async def start_joke(self, channel):
        if self.active:
            await channel.send("😅 One joke at a time~ let this one land.")
            return

        joke = await self._fetch_joke()
        if not joke:
            await channel.send("❌ I forgot the joke… awkward 🙈")
            return

        setup, punchline = joke
        self.current_punchline = punchline
        self.active = True
        self._answer_event.clear()

        prefix = random.choice(SARCASM_PREFIX)

        # send setup
        await channel.send(prefix)
        await channel.send(f"😂 {setup}")
        await channel.send("⏳ Tag me with your answer~")

        try:
            # wait for answer OR timeout
            await asyncio.wait_for(
                self._answer_event.wait(),
                timeout=ANSWER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            # no answer
            await channel.send("😌 Fine, I’ll say it myself.")
            await self._send_punchline(channel)

        self._reset()

    def notify_answer(self):
        if self.active:
            self._answer_event.set()

    def has_active_joke(self) -> bool:
        return self.active

    # =========================
    # INTERNAL
    # =========================

    async def _send_punchline(self, channel):
        delay = random.uniform(*PUNCHLINE_DELAY_RANGE)
        await asyncio.sleep(delay)

        suffix = random.choice(SARCASM_SUFFIX)

        await channel.send(f"👉 {self.current_punchline}")
        await channel.send(f"🖤 {suffix}")

    def _reset(self):
        self.active = False
        self.current_punchline = None
        self._answer_event.clear()

    async def _fetch_joke(self) -> tuple[str, str] | None:
        """
        Uses a SAFE joke API and applies sarcasm locally.
        """
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
