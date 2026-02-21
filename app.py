import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from dotenv import load_dotenv

# ❌ DISABLED FOR PHASE 1
# from twitch.twitch_chat import SharanTwitchBot

from twitch.eventsub import router as eventsub_router
from internal import router as internal_router   # 👈 ADD THIS

load_dotenv()

background_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Render EventSub service...")

    # ❌ DISABLED FOR PHASE 1
    # async def run_twitch():
    #     try:
    #         print("🎮 Starting Twitch bot...")
    #         twitch = SharanTwitchBot()
    #         await twitch.start_bot()
    #     except asyncio.CancelledError:
    #         print("🎮 Twitch bot shut down cleanly")
    #     except Exception as e:
    #         print("❌ Twitch bot crashed:", e)

    # ❌ DO NOT START TWITCH BOT ON RENDER
    # background_tasks.append(asyncio.create_task(run_twitch()))

    yield  # ⬅️ App is LIVE

    print("🛑 Shutting down Render service...")

    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)


# =========================
# 🌐 FASTAPI APP
# =========================

app = FastAPI(lifespan=lifespan)

# 🔗 EventSub routes (KEEP)
app.include_router(eventsub_router)

# 🔗 Internal polling routes (NEW)
app.include_router(internal_router)

# =========================
# ❤️ HEALTH CHECK
# =========================
@app.get("/")
async def root():
    return {"status": "EventSub service alive"}

@app.head("/")
async def head_root():
    return Response(status_code=200)