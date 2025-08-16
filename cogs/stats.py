import discord
from discord import app_commands
from discord.ext import commands
import psutil
import datetime
import platform
import os

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.start_time = datetime.datetime.now()

    @app_commands.command(name="stats", description="Show bot system stats")
    async def stats(self, interaction: discord.Interaction):
        # CPU and RAM
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        ram_percent = memory.percent

        # Uptime
        uptime = datetime.datetime.now() - self.start_time
        uptime_str = str(uptime).split(".")[0]  # remove microseconds

        # System info
        python_version = platform.python_version()
        system = platform.system()
        release = platform.release()

        embed = discord.Embed(
            title="📊 Bot Stats",
            color=discord.Color.blue()
        )
        embed.add_field(name="🖥️ CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="💾 RAM Usage", value=f"{ram_percent}%", inline=True)
        embed.add_field(name="⏳ Uptime", value=uptime_str, inline=False)
        embed.add_field(name="⚙️ System", value=f"{system} {release}", inline=True)
        embed.add_field(name="🐍 Python", value=python_version, inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Stats(client))
