# import discord
# from discord.ext import commands
# from discord import Embed, ui

# WELCOME_ROLE_ID = 1389613063107510282  # Your auto-role ID
# TWITCH_URL = "https://twitch.tv/sfrostuniverse"
# RULES_URL = "https://discord.com/channels/yourserverid/ruleschannelid"  # Replace with real channel link

# class WelcomeView(ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)
#         self.add_item(ui.Button(label="📺 Follow on Twitch", url=TWITCH_URL))
#         self.add_item(ui.Button(label="📜 Read Server Rules", url=RULES_URL))

# class Welcome(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.Cog.listener()
#     async def on_member_join(self, member: discord.Member):
#         try:
#             embed = Embed(
#                 title="💌 Welcome to the server, buddy!",
#                 description=(
#                     "I'm **Sharan**, your digital friend.\n"
#                     "Feel free to explore and say hi!\n\n"
#                     "⚡ Powered by **sFrostUniverse**"
#                 ),
#                 color=discord.Color.purple()
#             )
#             embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else discord.Embed.Empty)

#             await member.send(embed=embed, view=WelcomeView())

#             # Give the welcome role
#             role = member.guild.get_role(WELCOME_ROLE_ID)
#             if role:
#                 await member.add_roles(role)

#         except discord.Forbidden:
#             print(f"⚠️ Cannot DM or assign role to {member.name}")
#         except Exception as e:
#             print(f"❌ Error in welcome message: {e}")

# async def setup(bot):
#     await bot.add_cog(Welcome(bot))
