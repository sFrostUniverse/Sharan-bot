import discord
from discord import app_commands
from discord.ext import commands
import psutil
import datetime
import platform

class Stats(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.start_time = datetime.datetime.now()

    @app_commands.command(name="stats", description="Show bot system stats")
    @app_commands.guild_only()
    async def stats(self, interaction: discord.Interaction):
        # ✅ ACKNOWLEDGE IMMEDIATELY (prevents timeout)
        await interaction.response.defer(thinking=True)

        # CPU and RAM (psutil.cpu_percent with interval=1 blocks → OK after defer)
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        ram_percent = memory.percent

        # Uptime
        uptime = datetime.datetime.now() - self.start_time
        uptime_str = str(uptime).split(".")[0]

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

        # ✅ FOLLOW-UP response (never response.send_message after defer)
        await interaction.followup.send(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(Stats(client))
