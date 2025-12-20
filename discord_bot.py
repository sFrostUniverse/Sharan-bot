import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# ---------- BOT ----------
client = commands.Bot(command_prefix="!", intents=intents)


@client.event
async def setup_hook():
    """
    This runs BEFORE on_ready and is the correct place
    to load cogs and sync slash commands.
    """
    print("🔧 Discord setup_hook starting...")

    # Load cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"📦 Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")

    # Sync slash commands globally
    try:
        await client.tree.sync()
        print("🔁 Slash commands synced")
    except Exception as e:
        print("❌ Slash command sync failed:", e)


@client.event
async def on_ready():
    print(f"🤖 Sharan is online as {client.user} (ID: {client.user.id})")


async def start_discord_async():
    """
    Start the Discord bot WITHOUT blocking FastAPI.
    """
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set")

    await client.start(token)
