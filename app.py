import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from twitch.twitch_chat import SharanTwitchBot
from discord_bot import start_discord_async

load_dotenv()

# 🔒 Keep global references
twitch_bot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global twitch_bot

    print("🚀 Starting Sharan services...")

    twitch_bot = SharanTwitchBot()
    asyncio.create_task(twitch_bot.start_bot())

    asyncio.create_task(start_discord_async())

    yield  # 👈 App is running here

    print("🛑 Shutting down Sharan services...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"status": "Sharan is alive"}
