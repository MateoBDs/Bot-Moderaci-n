import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Comprueba si el bot funciona")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")

async def setup(bot):
    cog = Moderation(bot)
    await bot.add_cog(cog)
