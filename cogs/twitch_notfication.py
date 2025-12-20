import discord
from discord.ext import commands, tasks
from discord import ui
import aiohttp
import os
from dotenv import load_dotenv
import datetime as dt

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")

# 🟣 Multi-channel:role mapping
alert_mappings_env = os.getenv("TWITCH_ALERT_MAPPINGS", "")
TWITCH_ALERT_MAPPINGS: list[dict] = []

for mapping in alert_mappings_env.split(","):
    if ":" in mapping:
        channel_id, role_value = mapping.split(":")
        try:
            TWITCH_ALERT_MAPPINGS.append({
                "channel_id": int(channel_id.strip()),
                "role": role_value.strip()
            })
        except ValueError:
            print(f"⚠️ Invalid mapping skipped: {mapping}")

print("📡 Loaded Twitch alert mappings:", TWITCH_ALERT_MAPPINGS)

ANNOUNCEMENT_CHANNEL_ID = 1437440555490738176


# =========================
# 🔘 UI VIEWS
# =========================

class WatchStreamButton(ui.View):
    def __init__(self, twitch_url: str):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🔴 Watch Now", url=twitch_url))


class UpcomingStreamView(ui.View):
    def __init__(self, twitch_url: str):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🔔 Set Reminder on Twitch", url=twitch_url))


# =========================
# 🎮 MAIN COG
# =========================

class TwitchNotifications(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.access_token: str | None = None
        self.user_id: str | None = None

        self.stream_online = False
        self.last_stream_id: str | None = None

        self.last_schedule_id_30: str | None = None
        self.last_schedule_id_5: str | None = None

    # ⬇️ START TASKS ONLY WHEN BOT IS READY
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_stream.is_running():
            self.check_stream.start()
        if not self.check_schedule.is_running():
            self.check_schedule.start()
        print("🎮 Twitch notification tasks started")

    def cog_unload(self):
        self.check_stream.cancel()
        self.check_schedule.cancel()

    # =========================
    # 🔑 TWITCH AUTH
    # =========================

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
                    print(f"❌ Twitch token fetch failed: {resp.status}")
                    return
                data = await resp.json()
                self.access_token = data.get("access_token")

    async def get_user_id(self):
        if not self.access_token:
            return

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

    async def get_game_banner_url(self, game_id: str):
        if not self.access_token:
            return None

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
                    box = data["data"][0]["box_art_url"]
                    return box.replace("{width}", "640").replace("{height}", "360")
        return None

    # =========================
    # 🔴 LIVE CHECK
    # =========================

    @tasks.loop(seconds=60)
    async def check_stream(self):
        if not self.access_token:
            await self.get_access_token()
        if not self.user_id:
            await self.get_user_id()
        if not self.user_id:
            return

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
            stream = data["data"][0]
            if stream["id"] != self.last_stream_id:
                self.last_stream_id = stream["id"]
                self.stream_online = True
                await self.send_live_notification(stream)
                await self.update_channel_name(True)
        else:
            if self.stream_online:
                await self.update_channel_name(False)
                await self.bot.change_presence(activity=None)
            self.stream_online = False
            self.last_stream_id = None

    # =========================
    # 📢 LIVE NOTIFICATION
    # =========================

    async def send_live_notification(self, stream: dict):
        if not TWITCH_ALERT_MAPPINGS:
            return

        title = stream["title"]
        game_name = stream.get("game_name", "Unknown")
        game_id = stream.get("game_id")
        twitch_url = f"https://twitch.tv/{TWITCH_USERNAME}"

        banner = await self.get_game_banner_url(game_id) if game_id else None

        embed = discord.Embed(
            title=f"📺 {TWITCH_USERNAME} is now LIVE!",
            description=(
                f"🎮 **Playing:** {game_name}\n"
                f"📝 **Title:** *{title}*\n\n"
                f"🔴 Click below to watch live!"
            ),
            color=discord.Color.purple()
        )

        if banner:
            embed.set_image(url=banner)

        embed.set_footer(text="Powered by Sharan • Froséa")
        view = WatchStreamButton(twitch_url)

        for mapping in TWITCH_ALERT_MAPPINGS:
            channel = self.bot.get_channel(mapping["channel_id"])
            if not channel:
                continue

            await channel.send(
                content=f"<@&{mapping['role']}>",
                embed=embed,
                view=view,
                allowed_mentions=discord.AllowedMentions(roles=True)
            )

        await self.bot.change_presence(
            activity=discord.Streaming(
                name=f"Streaming now — {game_name} | itsfrosea",
                url=twitch_url
            )
        )

    # =========================
    # 📅 SCHEDULE CHECK
    # =========================

    @tasks.loop(minutes=5)
    async def check_schedule(self):
        if not self.access_token:
            await self.get_access_token()
        if not self.user_id:
            await self.get_user_id()
        if not self.user_id:
            return

        url = f"https://api.twitch.tv/helix/schedule?broadcaster_id={self.user_id}&first=1"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return
                data = await resp.json()

        segments = data.get("data", {}).get("segments") or []
        if not segments:
            self.last_schedule_id_30 = None
            self.last_schedule_id_5 = None
            return

        segment = segments[0]
        schedule_id = segment.get("id")
        start_str = segment.get("start_time")
        if not start_str:
            return

        start_time = dt.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        now_utc = dt.datetime.now(dt.timezone.utc)
        minutes_left = (start_time - now_utc).total_seconds() / 60

        if minutes_left <= 0:
            return

        ist_time = start_time + dt.timedelta(hours=5, minutes=30)
        ist_str = ist_time.strftime("%Y-%m-%d • %I:%M %p IST")

        title = segment.get("title", "Untitled stream")
        game_name = (segment.get("category") or {}).get("name", "TBA")
        twitch_url = f"https://twitch.tv/{TWITCH_USERNAME}"

        if 25 <= minutes_left <= 35 and self.last_schedule_id_30 != schedule_id:
            await self.send_schedule_notification(
                schedule_id, minutes_left, title, game_name, ist_str, twitch_url, "30 minutes"
            )
            self.last_schedule_id_30 = schedule_id

        if 3 <= minutes_left <= 7 and self.last_schedule_id_5 != schedule_id:
            await self.send_schedule_notification(
                schedule_id, minutes_left, title, game_name, ist_str, twitch_url, "5 minutes"
            )
            self.last_schedule_id_5 = schedule_id

    async def send_schedule_notification(
        self,
        schedule_id: str,
        minutes_left: float,
        title: str,
        game_name: str,
        ist_str: str,
        twitch_url: str,
        window_label: str
    ):
        embed = discord.Embed(
            title=f"📅 Upcoming Stream — {TWITCH_USERNAME}",
            description=(
                f"🕒 **Starts in:** ~{int(minutes_left)} minutes ({window_label})\n"
                f"📆 **Local time:** {ist_str}\n\n"
                f"📝 **Title:** *{title}*\n"
                f"🎮 **Game:** {game_name}"
            ),
            color=discord.Color.blurple()
        )

        view = UpcomingStreamView(twitch_url)

        for mapping in TWITCH_ALERT_MAPPINGS:
            channel = self.bot.get_channel(mapping["channel_id"])
            if not channel:
                continue

            await channel.send(
                content=f"<@&{mapping['role']}>",
                embed=embed,
                view=view,
                allowed_mentions=discord.AllowedMentions(roles=True)
            )

    # =========================
    # 📝 CHANNEL NAME
    # =========================

    async def update_channel_name(self, is_live: bool):
        channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if not channel:
            return

        new_name = "froséa-live🔴" if is_live else "froséa-offline"
        if channel.name != new_name:
            try:
                await channel.edit(name=new_name)
            except discord.Forbidden:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(TwitchNotifications(bot))
