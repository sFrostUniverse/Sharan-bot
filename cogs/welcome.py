import discord
from discord.ext import commands

ROLE_ID = 1389613063107510282  # Role to assign on join

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Send welcome DM
        try:
            embed = discord.Embed(
                title="👋 Welcome to the Server!",
                description="Hey buddy! I'm **Sharan**, your digital friend.\nFeel free to hang out and enjoy the server 😊",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="Powered by Sharan")
            await member.send(embed=embed)
        except discord.Forbidden:
            print(f"❌ Couldn't DM {member.name} — DMs might be disabled.")

        # Assign role
        role = member.guild.get_role(ROLE_ID)
        if role:
            try:
                await member.add_roles(role, reason="Auto welcome role by Sharan")
            except discord.Forbidden:
                print(f"❌ Missing permissions to add role to {member.name}.")
        else:
            print(f"❌ Role ID {ROLE_ID} not found in guild '{member.guild.name}'.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
