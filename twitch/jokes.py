# twitch/jokes.py

import asyncio
import aiohttp
import re

ANSWER_TIMEOUT = 30  # seconds


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


class JokeManager:
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.current_punchline: str | None = None
        self._normalized_answer: str | None = None
        self._winner: str | None = None
        self._answer_event = asyncio.Event()

    # =========================
    # PUBLIC API
    # =========================

    async def start_joke(self, channel):
        if self.active:
            await channel.send("😅 One joke at a time~")
            return

        joke = await self._fetch_joke()
        if not joke:
            await channel.send("❌ Joke machine broke 😭")
            return

        setup, punchline = joke
        self.current_punchline = punchline
        self._normalized_answer = normalize(punchline)
        self.active = True
        self._answer_event.clear()

        await channel.send(
            f"😂 {setup}  (type your answer or tag @Sharan)"
        )

        try:
            await asyncio.wait_for(
                self._answer_event.wait(),
                timeout=ANSWER_TIMEOUT,
            )

            if self._winner:
                await channel.send(
                    f"🎉 @{self._winner} got it!"
                )

            await channel.send(f"👉 {self.current_punchline}")

        except asyncio.TimeoutError:
            pass  # silent timeout

        self._reset()

    def try_answer(self, username: str, content: str):
        if not self.active or not self._normalized_answer:
            return False

        guess = normalize(content)

        # exact or near match
        if guess and guess in self._normalized_answer:
            self._winner = username
            self._answer_event.set()
            return True

        return False

    def force_answer(self):
        if self.active:
            self._answer_event.set()

    def has_active_joke(self) -> bool:
        return self.active

    # =========================
    # INTERNAL
    # =========================

    def _reset(self):
        self.active = False
        self.current_punchline = None
        self._normalized_answer = None
        self._winner = None
        self._answer_event.clear()

    async def _fetch_joke(self) -> tuple[str, str] | None:
        url = "https://official-joke-api.appspot.com/jokes/random"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    data = await resp.json()

            setup = data.get("setup")
            punchline = data.get("punchline")

            if setup and punchline:
                return setup.strip(), punchline.strip()

        except Exception as e:
            print("❌ Joke fetch failed:", e)

        return None
