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
DISCORD_CHANNEL_ID = int(os.getenv("TWITCH_ALERT_CHANNEL_ID", 0))
TWITCH_LIVE_ROLE_ID = int(os.getenv("TWITCH_LIVE_ROLE_ID", 0))  # ✅ Cast to int safely


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
        self.last_stream_id = None  # ✅ Track last stream to avoid duplicates
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
                if resp.status != 200:
                    print(f"❌ Failed to fetch Twitch token: {resp.status}")
                    return
                data = await resp.json()
                self.access_token = data.get("access_token")

    async def get_user_id(self):
        url = f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    print(f"❌ Failed to fetch user ID: {resp.status}")
                    return
                data = await resp.json()
                if data.get("data"):
                    self.user_id = data["data"][0]["id"]

    async def get_game_banner_url(self, game_id):
        url = f"https://api.twitch.tv/helix/games?id={game_id}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("data"):
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
                if resp.status != 200:
                    print(f"❌ Twitch stream check failed: {resp.status}")
                    return
                data = await resp.json()

                if data.get("data"):
                    stream_data = data["data"][0]

                    # ✅ Only send if this is a NEW stream
                    if stream_data["id"] != self.last_stream_id:
                        self.last_stream_id = stream_data["id"]
                        self.stream_online = True
                        await self.send_live_notification(stream_data)
                else:
                    if self.stream_online:
                        # stream just ended → reset presence
                        await self.bot.change_presence(activity=None)
                    self.stream_online = False
                    self.last_stream_id = None  # reset

    async def send_live_notification(self, stream):
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("❌ Discord channel not found!")
            return

        title = stream["title"]
        game_id = stream.get("game_id")
        game_name = stream.get("game_name", "Unknown")
        twitch_url = f"https://twitch.tv/{TWITCH_USERNAME}"

        banner_url = await self.get_game_banner_url(game_id) if game_id else None

        embed = discord.Embed(
            title=f"📺 {TWITCH_USERNAME} is now LIVE!",
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

        # ✅ Mention role safely (if set)
        role_mention = f"<@&{TWITCH_LIVE_ROLE_ID}>" if TWITCH_LIVE_ROLE_ID else None
        
        await channel.send(
            content=role_mention,
            embed=embed,
            view=WatchStreamButton(twitch_url),
            allowed_mentions=discord.AllowedMentions(roles=True)
        )

        # ✅ Update bot presence
        await self.bot.change_presence(activity=discord.Streaming(
            name=title,
            url=twitch_url
        ))


async def setup(bot):
    await bot.add_cog(TwitchNotifications(bot))
