import discord
from discord.ext import commands
from discord import app_commands


class SayCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="(Admin Only) Make the bot send a message to a channel or here."
    )
    @app_commands.guild_only()  # ✅ REQUIRED for permission checks
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        message="Enter the message (supports emojis or GIFs)",
        channel="Select the channel to send it in (optional)",
        reply_to="Reply to a specific message ID (optional)"
    )
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel | None = None,
        reply_to: str | None = None
    ):
        """Send a message as the bot."""

        # ✅ IMMEDIATELY acknowledge the interaction
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        print(
            f"🔔 /say executed by: {user} "
            f"| Display Name: {user.display_name} | ID: {user.id}"
        )

        target_channel = channel or interaction.channel

        try:
            if reply_to:
                target_message = await target_channel.fetch_message(int(reply_to))
                await target_message.reply(message)
                await interaction.followup.send(
                    f"💬 Replied in {target_channel.mention}", ephemeral=True
                )
            else:
                await target_channel.send(message)
                await interaction.followup.send(
                    f"📨 Message sent in {target_channel.mention}", ephemeral=True
                )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don’t have permission to send messages there.", ephemeral=True
            )

        except discord.NotFound:
            await interaction.followup.send(
                "⚠️ Could not find that message ID to reply to.", ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error: {e}", ephemeral=True
            )

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """
        Global error handler for this cog.
        Safely handles cases where the interaction
        was already deferred.
        """

        # Decide how we are allowed to respond
        if interaction.response.is_done():
            sender = interaction.followup.send
        else:
            sender = interaction.response.send_message

        if isinstance(error, app_commands.MissingPermissions):
            await sender(
                "⚠️ Only **Admins** can use this command.",
                ephemeral=True
            )
        else:
            await sender(
                f"❌ Error: {error}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(SayCommand(bot))
