import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands

DB_NAME = "data/database.db"
GUILD_ID = 1522869805462589593


class Setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="setup_logs")
    async def setup_logs(self, interaction: discord.Interaction, canal: discord.TextChannel):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
            INSERT OR REPLACE INTO guild_config (guild_id, logs_channel)
            VALUES (?, ?)
            """, (interaction.guild.id, canal.id))
            await db.commit()

        await interaction.followup.send(f"✅ Logs: {canal.mention}")


    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="setup_sanciones")
    async def setup_sanciones(self, interaction: discord.Interaction, canal: discord.TextChannel):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
            INSERT OR REPLACE INTO guild_config (guild_id, punishments_channel)
            VALUES (?, ?)
            """, (interaction.guild.id, canal.id))
            await db.commit()

        await interaction.followup.send(f"✅ Sanciones: {canal.mention}")


    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="setup_modrole")
    async def setup_modrole(self, interaction: discord.Interaction, role: discord.Role):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
            INSERT OR REPLACE INTO guild_config (guild_id, mod_role)
            VALUES (?, ?)
            """, (interaction.guild.id, role.id))
            await db.commit()

        await interaction.followup.send(f"✅ Mod role: {role.mention}")


async def setup(bot):
    await bot.add_cog(Setup(bot))
