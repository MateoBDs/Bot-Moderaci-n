import discord
import aiosqlite
import datetime

from discord.ext import commands
from discord import app_commands

DB_NAME = "data/database.db"
GUILD_ID = 1522869805462589593


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")


    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="warn")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute("""
            INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
            VALUES (?, ?, ?, ?)
            """, (interaction.guild.id, usuario.id, interaction.user.id, razon))

            await db.commit()

        await interaction.followup.send(f"⚠️ Warn a {usuario.mention}")


    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="warnings")
    async def warnings(self, interaction: discord.Interaction, usuario: discord.Member):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute("""
            SELECT id, moderator_id, reason, created_at
            FROM warnings
            WHERE guild_id = ? AND user_id = ?
            ORDER BY id DESC
            """, (interaction.guild.id, usuario.id))

            warns = await cursor.fetchall()

        if not warns:
            return await interaction.followup.send("Sin warns")

        embed = discord.Embed(
            title=f"Warnings {usuario.display_name}",
            color=discord.Color.orange()
        )

        text = ""

        for wid, mod, reason, created in warns:

            try:
                ts = int(datetime.datetime.strptime(
                    created, "%Y-%m-%d %H:%M:%S"
                ).timestamp())
            except:
                ts = 0

            text += f"#{wid} | <@{mod}> | {reason} | <t:{ts}:F>\n"

        embed.description = text

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
