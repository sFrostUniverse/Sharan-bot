from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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

if __name__ == "__main__":
    client.run(TOKEN)
