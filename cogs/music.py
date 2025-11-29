import discord
from discord.ext import commands
import yt_dlp

YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


# ============================
# 🎚 BUTTON CONTROLLER VIEW
# ============================

class MusicController(discord.ui.View):
    def __init__(self, vc):
        super().__init__(timeout=None)
        self.vc = vc

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.gray)
    async def pause_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.vc.is_playing():
            return await interaction.response.send_message("⚠ Nothing is playing.", ephemeral=True)
        self.vc.pause()
        await interaction.response.send_message("⏸ Paused.", ephemeral=True)

    @discord.ui.button(label="▶ Resume", style=discord.ButtonStyle.green)
    async def resume_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.vc.is_paused():
            return await interaction.response.send_message("⚠ Music is not paused.", ephemeral=True)
        self.vc.resume()
        await interaction.response.send_message("▶ Resumed.", ephemeral=True)

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.blurple)
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (self.vc.is_playing() or self.vc.is_paused()):
            return await interaction.response.send_message("⚠ Nothing to skip.", ephemeral=True)
        self.vc.stop()
        await interaction.response.send_message("⏭ Skipped.", ephemeral=True)

    @discord.ui.button(label="⛔ Stop", style=discord.ButtonStyle.red)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (self.vc.is_playing() or self.vc.is_paused()):
            return await interaction.response.send_message("⚠ Nothing to stop.", ephemeral=True)
        self.vc.stop()
        await interaction.response.send_message("⛔ Stopped.", ephemeral=True)


# ============================
# 🎵 MUSIC COG
# ============================

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("❌ You're not in any voice channel!")
            return None

        if ctx.voice_client is None:
            return await ctx.author.voice.channel.connect()

        return ctx.voice_client

    @commands.command()
    async def play(self, ctx, *, search: str = None):
        if search is None:
            return await ctx.send("⚠ You must enter a song name!\nExample: `!play believer`")

        vc = await self.ensure_voice(ctx)
        if vc is None:
            return

        if vc.is_playing():
            vc.stop()

        # Search YouTube
        try:
            with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                entry = info["entries"][0]
                url = entry["url"]
                title = entry["title"]
        except Exception as e:
            return await ctx.send(f"❌ Failed to load audio: `{e}`")

        # Play audio
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTS)
        vc.play(source)

        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"**{title}**",
            color=discord.Color.purple()
        )

        view = MusicController(vc)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel.")
        else:
            await ctx.send("❌ I'm not connected to any voice channel.")

    # Global error handler for music commands
    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠ You must enter a song!\nExample: `!play shape of you`")
        else:
            await ctx.send(f"❌ Error: {error}")


async def setup(bot):
    await bot.add_cog(Music(bot))
