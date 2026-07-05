import discord
import aiosqlite
import datetime

from discord.ext import commands
from discord import app_commands

from utils.permissions import is_mod
from utils.logs import send_log, send_punishment, send_dm

DB_NAME = "data/database.db"
GUILD_ID = 1522869805462589593


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.command(name="warn")
async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):

    await interaction.response.defer()

    if not await is_mod(interaction.user):
        return await interaction.followup.send("❌ No perms")

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
        VALUES (?, ?, ?, ?)
        """, (interaction.guild.id, user.id, interaction.user.id, reason))

        await db.execute("""
        INSERT INTO punishments (guild_id, user_id, moderator_id, action, reason)
        VALUES (?, ?, ?, ?, ?)
        """, (interaction.guild.id, user.id, interaction.user.id, "WARN", reason))

        await db.commit()

    # =========================
    # EMBED (TU FORMATO)
    # =========================
    embed = discord.Embed(
        description=f"""# ⚠️ WARN ⚠️
🠺 🧑Usuario: {user.name}
🠺 💻Moderador: {interaction.user.mention}
🠺 ✉Razón: {reason}

> Si crees que tu sanción fué injusta, puedes abrir ticket en <#1522869806540259350>.

-# BDcell © 2026 | Moderación""",
        color=discord.Color.orange()
    )

    # =========================
    # MENSAJE FUERA DEL EMBED
    # =========================
    await interaction.channel.send(
        f"{user.mention} <@&1523282618408501358>",
        embed=embed
    )

    # =========================
    # LOGS + DM
    # =========================
    await send_punishment(interaction.guild, user.mention, embed)
    await send_log(interaction.guild, embed)
    await send_dm(user, embed)

    await interaction.followup.send("✅ Warn aplicado")

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="warnings")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute("""
            SELECT id, moderator_id, reason, created_at
            FROM warnings
            WHERE guild_id = ? AND user_id = ?
            """, (interaction.guild.id, user.id))

            rows = await cursor.fetchall()

        if not rows:
            return await interaction.followup.send("Sin warns")

        text = ""
        for r in rows:
            text += f"#{r[0]} | <@{r[1]}> | {r[2]} | <t:{int(datetime.datetime.now().timestamp())}:F>\n"

        embed = discord.Embed(
            title="Warnings",
            description=text,
            color=discord.Color.orange()
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
