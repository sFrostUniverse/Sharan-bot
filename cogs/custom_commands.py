import discord
from discord.ext import commands
from discord import app_commands

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Admin-only Shoutout command
    @app_commands.command(name="shoutout", description="Give a shoutout to a Twitch streamer")
    @app_commands.checks.has_permissions(administrator=True)
    async def shoutout(self, interaction: discord.Interaction, user: str):
        await interaction.response.send_message(
            f"🎉 Big shoutout to [{user}](https://twitch.tv/{user})! Go check out their stream!", 
            ephemeral=False
        )

    @app_commands.command(name="socials", description="Get all my social links")
    async def socials(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🌐 **Follow Sehaj Everywhere:**\n"
            "- Twitch: https://twitch.tv/YOURUSERNAME\n"
            "- Instagram: https://instagram.com/YOURUSERNAME\n"
            "- Twitter: https://twitter.com/YOURUSERNAME",
            ephemeral=False
        )

    @app_commands.command(name="commands", description="List available custom commands")
    async def commands_list(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "📋 **Custom Commands Available:**\n"
            "- `/shoutout <user>` (Admin only)\n"
            "- `/socials`\n"
            "- `/commands`", 
            ephemeral=True
        )

    # ✅ Custom error handler for app_commands
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "⚠️ Sorry, only **Admins** can use this command.",
                ephemeral=True
            )
        else:
            # fallback for other errors
            await interaction.response.send_message(
                f"❌ An error occurred: {error}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
