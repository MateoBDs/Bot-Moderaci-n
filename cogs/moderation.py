import discord
import aiosqlite
import datetime

from discord.ext import commands
from discord import app_commands

from utils.permissions import is_mod
from utils.logs import send_log, send_punishment

DB_NAME = "data/database.db"
GUILD_ID = 1522869805462589593


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # =========================
    # /WARN
    # =========================
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="warn")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):

        await interaction.response.defer()

        if not await is_mod(interaction.user):
            return await interaction.followup.send("❌ No permisos")

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
        # CANAL SANCIONES (TU PLANTILLA)
        # =========================
        sanction_embed = discord.Embed(
            description=f"""# ⚠️ WARN ⚠️
-# <@&1523282618408501358>

🠺 🧑Usuario: {user.name}
🠺 💻Moderador: {interaction.user.mention}
🠺 ✉Razón: {reason}

> Si crees que tu sanción fué injusta, puedes abrir ticket en <#1522869806540259350> .

-# BDcell © 2026 | Moderación""",
            color=discord.Color.orange()
        )

        await send_punishment(interaction.guild, sanction_embed)

        # =========================
        # LOGS (TÉCNICO)
        # =========================
        log_embed = discord.Embed(
            title="WARN LOG",
            description=f"""
User: {user} ({user.id})
Mod: {interaction.user} ({interaction.user.id})
Reason: {reason}
""",
            color=discord.Color.dark_orange()
        )

        await send_log(interaction.guild, log_embed)

        # =========================
        # DM USUARIO
        # =========================
        try:
            dm = discord.Embed(
                title="⚠ Has sido sancionado",
                description=f"""
Has recibido un **WARN** en {interaction.guild.name}

✉ Razón: {reason}
👮 Moderador: {interaction.user.name}
""",
                color=discord.Color.red()
            )
            await user.send(embed=dm)
        except:
            pass

        # =========================
        # SOLO CONFIRMACIÓN EN CANAL
        # =========================
        await interaction.followup.send(f"✅ Warn aplicado a {user.mention}")


    # =========================
    # /WARNINGS
    # =========================
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="warnings")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):

        await interaction.response.defer()

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute("""
            SELECT id, moderator_id, reason, created_at
            FROM warnings
            WHERE guild_id = ? AND user_id = ?
            ORDER BY id DESC
            """, (interaction.guild.id, user.id))

            rows = await cursor.fetchall()

        if not rows:
            return await interaction.followup.send("Sin warnings")

        embed = discord.Embed(
            title=f"📜 Warnings de {user.name}",
            color=discord.Color.orange()
        )

        text = ""

        for wid, mod, reason, created in rows:

            try:
                ts = int(datetime.datetime.strptime(
                    created, "%Y-%m-%d %H:%M:%S"
                ).timestamp())
            except:
                ts = 0

            text += f"#{wid} | <@{mod}> | {reason} | <t:{ts}:F>\n"

        embed.description = text

        await interaction.followup.send(embed=embed)


    # =========================
    # /UNWARN
    # =========================
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(name="unwarn")
    async def unwarn(self, interaction: discord.Interaction, warn_id: int):

        await interaction.response.defer()

        if not await is_mod(interaction.user):
            return await interaction.followup.send("❌ No permisos")

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute("""
            SELECT user_id
            FROM warnings
            WHERE id = ? AND guild_id = ?
            """, (warn_id, interaction.guild.id))

            data = await cursor.fetchone()

            if not data:
                return await interaction.followup.send("❌ Warn no encontrado")

            user_id = data[0]

            await db.execute("""
            DELETE FROM warnings
            WHERE id = ? AND guild_id = ?
            """, (warn_id, interaction.guild.id))

            await db.execute("""
            INSERT INTO punishments (guild_id, user_id, moderator_id, action, reason)
            VALUES (?, ?, ?, ?, ?)
            """, (
                interaction.guild.id,
                user_id,
                interaction.user.id,
                "UNWARN",
                f"Removed warn {warn_id}"
            ))

            await db.commit()

        log = discord.Embed(
            title="UNWARN",
            description=f"Warn `{warn_id}` eliminado por {interaction.user.mention}",
            color=discord.Color.red()
        )

        await send_log(interaction.guild, log)

        await interaction.followup.send("✅ Warn eliminado")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
