import discord
from discord.ext import commands, tasks
from discord import ui
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")

# 🟣 Multi-channel:role mapping (supports different role per server)
alert_mappings_env = os.getenv("TWITCH_ALERT_MAPPINGS", "")
TWITCH_ALERT_MAPPINGS = []

for mapping in alert_mappings_env.split(","):
    if ":" in mapping:
        channel_id, role_value = mapping.split(":")
        try:
            channel_id = int(channel_id.strip())
            role_value = role_value.strip()
            TWITCH_ALERT_MAPPINGS.append({
                "channel_id": channel_id,
                "role": role_value  # role ID as string
            })
        except ValueError:
            print(f"⚠️ Invalid mapping skipped: {mapping}")

print("📡 Loaded Twitch alert mappings:", TWITCH_ALERT_MAPPINGS)

# ✅ Your announcement channel ID (the one to rename)
ANNOUNCEMENT_CHANNEL_ID = 1437440555490738176


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
        self.last_stream_id = None
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
                    if stream_data["id"] != self.last_stream_id:
                        self.last_stream_id = stream_data["id"]
                        self.stream_online = True
                        await self.send_live_notification(stream_data)
                        await self.update_channel_name(is_live=True)
                else:
                    if self.stream_online:
                        await self.bot.change_presence(activity=None)
                        await self.update_channel_name(is_live=False)
                    self.stream_online = False
                    self.last_stream_id = None

    async def send_live_notification(self, stream):
        if not TWITCH_ALERT_MAPPINGS:
            print("❌ No Twitch alert mappings configured!")
            return

        title = stream["title"]
        game_id = stream.get("game_id")
        game_name = stream.get("game_name", "Unknown")
        twitch_url = f"https://twitch.tv/{TWITCH_USERNAME}"

        banner_url = await self.get_game_banner_url(game_id) if game_id else None

        embed = discord.Embed(
            title=f"📺 {TWITCH_USERNAME} is now LIVE!",
            description=(f"🎮 **Playing:** {game_name}\n"
                         f"📝 **Title:** *{title}*\n\n"
                         f"🔴 Click the button below to watch live!"),
            color=discord.Color.purple()
        )

        if banner_url:
            embed.set_image(url=banner_url)

        embed.set_footer(text="Powered by Sharan • Froséa")
        view = WatchStreamButton(twitch_url)

        for mapping in TWITCH_ALERT_MAPPINGS:
            channel_id = mapping["channel_id"]
            role_value = mapping["role"]

            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"⚠️ Channel {channel_id} not found or not cached.")
                continue

            role_mention = f"<@&{role_value}>"
            allowed_mentions = discord.AllowedMentions(roles=True)

            try:
                await channel.send(
                    content=role_mention,
                    embed=embed,
                    view=view,
                    allowed_mentions=allowed_mentions
                )
                print(f"✅ Sent LIVE alert to {channel.name} ({channel.id}) → Mentioned {role_mention}")
            except Exception as e:
                print(f"❌ Failed to send to {channel_id}: {e}")

        # 🟣 Update bot presence with game name + your name
        presence_text = f"Streaming now — {game_name} | itsfrosea"

        await self.bot.change_presence(
            activity=discord.Streaming(
                name=presence_text,
                url=twitch_url
            )
        )


    async def update_channel_name(self, is_live: bool):
        """Change the announcement channel name depending on stream status."""
        channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if not channel:
            print(f"⚠️ Announcement channel {ANNOUNCEMENT_CHANNEL_ID} not found.")
            return

        new_name = "🟢froséa-live🟢" if is_live else "🔴froséa-live🔴"

        try:
            if channel.name != new_name:
                await channel.edit(name=new_name)
                print(f"✅ Updated announcement channel name to: {new_name}")
        except discord.Forbidden:
            print("❌ Missing permission to rename the channel.")
        except Exception as e:
            print(f"❌ Failed to rename channel: {e}")


async def setup(bot):
    await bot.add_cog(TwitchNotifications(bot))
