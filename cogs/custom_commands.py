import discord
from discord.ext import commands
from discord import app_commands

class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="say", description="(Admin Only) Make the bot say something.")
    @app_commands.checks.has_permissions(administrator=True)
    async def say(self, interaction: discord.Interaction, message: str):
        """
        Admin-only /say command.
        Sends the message through the bot without showing who used it.
        """

        # Hide the command execution
        await interaction.response.defer(ephemeral=True)

        # Bot speaks in the channel
        await interaction.channel.send(message)

        # Only you see this confirmation
        await interaction.followup.send("✅ Message sent.", ephemeral=True)

    # Handle errors (like missing admin permission)
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "⚠️ Only **Admins** can use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Error: {error}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(SayCommand(bot))
