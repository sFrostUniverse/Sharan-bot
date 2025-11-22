import discord
from discord.ext import commands
from discord import app_commands

class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="(Admin Only) Make the bot send a message to a channel or here."
    )
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
        channel: discord.TextChannel = None,
        reply_to: str = None
    ):
        """
        Admin-only /say command.
        Sends a message (or reply) to any channel — or same one if none chosen.
        """

        # Acknowledge the interaction safely
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        # 🟣 Log to terminal
        user = interaction.user
        print(f"📝 /say used by: {user} | Display Name: {user.display_name} | ID: {user.id}")

        # If no channel selected, send in the same channel where the command was used
        target_channel = channel or interaction.channel

        try:
            if reply_to:
                target_message = await target_channel.fetch_message(int(reply_to))
                await target_message.reply(message)
                await interaction.followup.send(
                    f"✅ Replied in {target_channel.mention}", ephemeral=True
                )
            else:
                await target_channel.send(message)
                await interaction.followup.send(
                    f"✅ Message sent in {target_channel.mention}", ephemeral=True
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

    # Correct error handler — using followup instead of response
    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.followup.send(
                "⚠️ Only **Admins** can use this command.", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Error: {error}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(SayCommand(bot))
