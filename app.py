import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from dotenv import load_dotenv

from twitch.twitch_chat import SharanTwitchBot
from discord_bot import start_discord_async

load_dotenv()

# Keep references so tasks are not garbage-collected
background_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Sharan services...")

    async def run_twitch():
        try:
            print("🎮 Starting Twitch bot...")
            twitch = SharanTwitchBot()
            await twitch.start_bot()
        except asyncio.CancelledError:
            print("🎮 Twitch bot shut down cleanly")
        except Exception as e:
            print("❌ Twitch bot crashed:", e)

    async def run_discord():
        try:
            print("🤖 Starting Discord bot...")
            await start_discord_async()
        except asyncio.CancelledError:
            print("🤖 Discord bot shut down cleanly")
        except Exception as e:
            print("❌ Discord bot crashed:", e)

    # Start bots as background tasks
    background_tasks.append(asyncio.create_task(run_twitch()))
    background_tasks.append(asyncio.create_task(run_discord()))

    yield  # ⬅️ Application is LIVE here

    print("🛑 Shutting down Sharan services...")

    # Gracefully cancel background tasks
    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "Sharan is alive"}


@app.head("/")
async def head_root():
    return Response(status_code=200)
