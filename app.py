import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from dotenv import load_dotenv

from twitch.twitch_chat import SharanTwitchBot
from discord_bot import start_discord_async

load_dotenv()

twitch_bot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global twitch_bot

    print("🚀 Starting Sharan services...")

    async def run_twitch():
        try:
            twitch = SharanTwitchBot()
            await twitch.start_bot()
        except Exception as e:
            print("❌ Twitch bot crashed:", e)

    async def run_discord():
        try:
            await start_discord_async()
        except Exception as e:
            print("❌ Discord bot crashed:", e)

    asyncio.create_task(run_twitch())
    asyncio.create_task(run_discord())

    yield  # App is live here

    print("🛑 Shutting down Sharan services...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "Sharan is alive"}


@app.head("/")
async def head_root():
    return Response(status_code=200)
