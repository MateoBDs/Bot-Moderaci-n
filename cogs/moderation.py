import discord
from discord.ext import commands
from discord import app_commands

GUILD_ID = 1522869805462589593


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="ping",
        description="Comprueba si el bot funciona"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🏓 Pong!"
        )
    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="test",
        description="Comando de prueba"
    )
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(
        "✅ El cog funciona correctamente."
        )

async def setup(bot):
    await bot.add_cog(
        Moderation(bot)
    )
