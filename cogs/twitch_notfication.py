import discord
from discord.ext import commands, tasks
from discord import ui
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")  # your twitch username (no @)
DISCORD_CHANNEL_ID = int(os.getenv("TWITCH_ALERT_CHANNEL_ID"))

class WatchStreamButton(ui.View):
    def __init__(self, twitch_url: str):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🔴 Watch Now", url=twitch_url))

class TwitchNotifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.access_token = None
        self.user_id = None
        self.stream_online = False
        self.check_stream.start()

    def cog_unload(self):
        self.check_stream.cancel()

    async def get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                data = await resp.json()
                self.access_token = data["access_token"]

    async def get_user_id(self):
        url = f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                self.user_id = data["data"][0]["id"]

    async def get_game_banner_url(self, game_id):
        url = f"https://api.twitch.tv/helix/games?id={game_id}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data["data"]:
                    box_art_url = data["data"][0]["box_art_url"]
                    return box_art_url.replace("{width}", "640").replace("{height}", "360")
        return None

    @tasks.loop(seconds=60)
    async def check_stream(self):
        if not self.access_token or not self.user_id:
            await self.get_access_token()
            await self.get_user_id()

        url = f"https://api.twitch.tv/helix/streams?user_id={self.user_id}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data["data"]:
                    if not self.stream_online:
                        self.stream_online = True
                        stream_data = data["data"][0]
                        await self.send_live_notification(stream_data)
                else:
                    self.stream_online = False

    async def send_live_notification(self, stream):
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        title = stream["title"]
        game_id = stream.get("game_id")
        game_name = stream.get("game_name", "Unknown")
        twitch_url = f"https://twitch.tv/{TWITCH_USERNAME}"

        banner_url = await self.get_game_banner_url(game_id) if game_id else None

        embed = discord.Embed(
            title="📺 sFrostUniverse is now LIVE!",
            description=(
                f"🎮 **Playing:** {game_name}\n"
                f"📝 **Title:** *{title}*\n\n"
                f"🔴 Click the button below to watch live!"
            ),
            color=discord.Color.purple()
        )

        if banner_url:
            embed.set_image(url=banner_url)

        embed.set_footer(text="Powered by Sharan • sFrostUniverse")

        await channel.send(embed=embed, view=WatchStreamButton(twitch_url))

async def setup(bot):
    await bot.add_cog(TwitchNotifications(bot))
