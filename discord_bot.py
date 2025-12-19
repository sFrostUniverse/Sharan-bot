import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"🤖 Sharan is online as {client.user}")

async def start_discord_async():
    await client.start(os.getenv("DISCORD_TOKEN"))
