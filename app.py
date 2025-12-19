import asyncio
import os
from fastapi import FastAPI
from dotenv import load_dotenv

from twitch.twitch_chat import SharanTwitchBot
from discord_bot import start_discord_async

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Sharan is alive"}

@app.on_event("startup")
async def startup():
    print("🚀 Starting Sharan services...")

    twitch_bot = SharanTwitchBot()
    asyncio.create_task(twitch_bot.start_bot())

    asyncio.create_task(start_discord_async())
