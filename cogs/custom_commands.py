import discord
from discord.ext import commands
from discord import app_commands

class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="(Admin Only) Make the bot send a message to a chosen channel."
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        channel="Select the channel to send the message",
        message="Enter the message, you can include emojis or GIF links",
        reply_to="Reply to a specific message ID (optional)"
    )
    async def say(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        reply_to: str = None
    ):
        """
        Admin-only /say command.
        Lets you send messages (with emojis, GIFs, or replies) to any channel silently.
        """

        await interaction.response.defer(ephemeral=True)

        try:
            if reply_to:
                # Try to fetch message to reply to
                target_msg = await channel.fetch_message(int(reply_to))
                await target_msg.reply(message)
                await interaction.followup.send(
                    f"✅ Replied in {channel.mention}", ephemeral=True
                )
            else:
                # Normal message send
                await channel.send(message)
                await interaction.followup.send(
                    f"✅ Message sent in {channel.mention}", ephemeral=True
                )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don’t have permission to send messages in that channel.",
                ephemeral=True
            )

        except discord.NotFound:
            await interaction.followup.send(
                "⚠️ Could not find that message ID to reply to.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error sending message: {e}", ephemeral=True
            )

    # Handle permission errors cleanly
    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "⚠️ Only **Admins** can use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Error: {error}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(SayCommand(bot))
