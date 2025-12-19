import os
import threading
import discord
from discord.ext import commands
from dotenv import load_dotenv
import uvicorn

from twitch.twitch_chat import SharanTwitchBot
from twitch.eventsub import app as twitch_eventsub_app

load_dotenv()

# ---------------- DISCORD SETUP ----------------

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await client.load_extension(f"cogs.{filename[:-3]}")

@client.event
async def setup_hook():
    await load_cogs()
    await client.tree.sync()

@client.event
async def on_ready():
    print(f"🤖 Sharan is online as {client.user}")

def run_discord():
    client.run(TOKEN)

# ---------------- EVENTSUB SERVER ----------------

def run_eventsub():
    uvicorn.run(
        twitch_eventsub_app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )

# ---------------- MAIN ENTRY ----------------

if __name__ == "__main__":
    # 1️⃣ Start Discord in background thread
    discord_thread = threading.Thread(target=run_discord, daemon=True)
    discord_thread.start()

    # 2️⃣ Start EventSub in background thread
    # eventsub_thread = threading.Thread(target=run_eventsub, daemon=True)
    # eventsub_thread.start()

    # 3️⃣ Start TwitchIO in MAIN THREAD (CRITICAL)
    twitch_bot = SharanTwitchBot()
    twitch_bot.run()
