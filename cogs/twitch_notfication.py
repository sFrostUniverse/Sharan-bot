import discord
from discord.ext import commands, tasks
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
DISCORD_CHANNEL_ID = int(os.getenv("TWITCH_ALERT_CHANNEL_ID"))

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
                    # Stream is live
                    if not self.stream_online:
                        self.stream_online = True
                        stream_data = data["data"][0]
                        await self.send_live_notification(stream_data)
                else:
                    # Stream is offline
                    if self.stream_online:
                        self.stream_online = False
                        await self.bot.change_presence(activity=None)

    async def send_live_notification(self, stream):
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            title = stream["title"]
            url = f"https://twitch.tv/{TWITCH_USERNAME}"

            # Update bot presence to "Streaming"
            await self.bot.change_presence(
                activity=discord.Streaming(name=title, url=url)
            )

            # Send notification to alert channel
            await channel.send(
                f"🔴 **{TWITCH_USERNAME} is now live!**\n"
                f"**Title:** {title}\n"
                f"{url}"
            )

async def setup(bot):
    await bot.add_cog(TwitchNotifications(bot))
