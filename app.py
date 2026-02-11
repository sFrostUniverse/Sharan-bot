import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from dotenv import load_dotenv

from twitch.twitch_chat import SharanTwitchBot
from twitch.eventsub import router as eventsub_router

load_dotenv()

background_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Twitch services (Render)...")

    async def run_twitch():
        try:
            print("🎮 Starting Twitch bot...")
            twitch = SharanTwitchBot()
            await twitch.start_bot()
        except asyncio.CancelledError:
            print("🎮 Twitch bot shut down cleanly")
        except Exception as e:
            print("❌ Twitch bot crashed:", e)

    # ✅ ONLY Twitch runs on Render
    background_tasks.append(asyncio.create_task(run_twitch()))

    yield  # ⬅️ App is LIVE

    print("🛑 Shutting down Twitch services...")

    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)


# =========================
# 🌐 FASTAPI APP
# =========================

app = FastAPI(lifespan=lifespan)

# 🔗 EventSub routes (KEEP)
app.include_router(eventsub_router)


# =========================
# ❤️ HEALTH CHECK
# =========================
@app.get("/")
async def root():
    return {"status": "Twitch service alive"}

@app.head("/")
async def head_root():
    return Response(status_code=200)