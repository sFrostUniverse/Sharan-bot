import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

from keep_alive import keep_alive

keep_alive()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed for member join and role assignment

# Initialize bot client
client = commands.Bot(command_prefix="!", intents=intents)
client.synced = False


# Load all cogs from /cogs directory
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")


# Proper v2.x setup hook (runs before on_ready)
@client.event
async def setup_hook():
    await load_cogs()
    try:
        synced = await client.tree.sync()
        print(f"🌍 Globally synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")


# When the bot is ready
@client.event
async def on_ready():
    print(f"🤖 Sharan is online as {client.user} (ID: {client.user.id})")



if __name__ == "__main__":
    client.run(TOKEN)
