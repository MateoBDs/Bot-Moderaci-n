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
    @app_commands.command(name="setup")
    async def setup(self, interaction: discord.Interaction,
                    logs: discord.TextChannel,
                    sanciones: discord.TextChannel,
                    modrole: discord.Role):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute("""
            INSERT INTO guild_config (guild_id, logs_channel, punishments_channel, mod_role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
            logs_channel=excluded.logs_channel,
            punishments_channel=excluded.punishments_channel,
            mod_role=excluded.mod_role
            """, (
                interaction.guild.id,
                logs.id,
                sanciones.id,
                modrole.id
            ))

            await db.commit()

        await interaction.followup.send("✅ Setup completo")


async def setup(bot):
    await bot.add_cog(Setup(bot))
