from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import threading

from twitch.twitch_chat import run_twitch
from twitch.eventsub import app as twitch_eventsub_app
import uvicorn
import threading


load_dotenv()
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

def run_eventsub():
    uvicorn.run(
        twitch_eventsub_app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )

if __name__ == "__main__":
    # Start Twitch chat bot (stable v2)
    twitch_thread = threading.Thread(target=run_twitch, daemon=True)
    twitch_thread.start()

    # Start Discord bot
    client.run(TOKEN)

