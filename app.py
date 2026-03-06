import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from dotenv import load_dotenv

from twitch.oauth import router as oauth_router
from twitch.eventsub import router as eventsub_router
from internal import router as internal_router
from render_routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

background_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Render EventSub service...")

    yield

    print("🛑 Shutting down Render service...")

    for task in background_tasks:
        task.cancel()

    await asyncio.gather(*background_tasks, return_exceptions=True)


# =========================
# 🌐 FASTAPI APP
# =========================

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 ROUTERS
app.include_router(oauth_router)
app.include_router(eventsub_router)
app.include_router(internal_router)
app.include_router(api_router)   # Dashboard API routes


# =========================
# ❤️ HEALTH CHECK
# =========================

@app.get("/")
async def root():
    return {"status": "EventSub service alive"}


@app.head("/")
async def head_root():
    return Response(status_code=200)