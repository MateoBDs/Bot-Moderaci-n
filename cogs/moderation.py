import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands

from utils.permissions import is_mod
from utils.logs import send_log, send_punishment, send_dm

DB_NAME = "database.db"
GUILD_ID = 1522869805462589593


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # /ping
    # -------------------------
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="ping",
        description="Comprueba si el bot funciona"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")

    # -------------------------
    # /warn
    # -------------------------
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="warn",
        description="Dar advertencia a un usuario"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str
    ):

        if not await is_mod(interaction.user):
            return await interaction.response.send_message(
                "❌ No tienes permisos.",
                ephemeral=True
            )

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute("""
                INSERT INTO warnings (
                    guild_id, user_id, moderator_id, reason
                ) VALUES (?, ?, ?, ?)
            """, (
                interaction.guild.id,
                usuario.id,
                interaction.user.id,
                razon
            ))

            await db.execute("""
                INSERT INTO punishments (
                    guild_id, user_id, moderator_id, action, reason
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                interaction.guild.id,
                usuario.id,
                interaction.user.id,
                "WARN",
                razon
            ))

            await db.commit()

        embed = discord.Embed(
            title="⚠️ WARN ⚠️",
            color=discord.Color.orange()
        )

        embed.description = (
            f"🠺 🧑 **Usuario:** {usuario.display_name}\n"
            f"🠺 💻 **Moderador:** {interaction.user.mention}\n"
            f"🠺 ✉ **Razón:** {razon}\n\n"
            f"> Si crees que tu sanción fue injusta, abre ticket en <#1522869806540259350>\n\n"
            f"-# BDcell © 2026 | Moderación"
        )

        await send_punishment(
            interaction.guild,
            f"<@&1523282618408501358> {usuario.mention}",
            embed
        )

        dm = discord.Embed(
            title="⚠️ Advertencia recibida",
            color=discord.Color.orange()
        )

        dm.description = f"Servidor: {interaction.guild.name}\nRazón: {razon}"

        await send_dm(usuario, dm)

        log = discord.Embed(
            title="📌 WARN LOG",
            color=discord.Color.orange()
        )

        log.add_field(name="Usuario", value=f"{usuario} ({usuario.id})", inline=False)
        log.add_field(name="Moderador", value=f"{interaction.user}", inline=False)
        log.add_field(name="Razón", value=razon, inline=False)

        await send_log(interaction.guild, log)

        await interaction.response.send_message(
            f"✅ Warn aplicado a {usuario.mention}"
        )

    # -------------------------
    # /warnings (con HAMMER TIME)
    # -------------------------
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="warnings",
        description="Ver advertencias de un usuario"
    )
    async def warnings(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        if not await is_mod(interaction.user):
            return await interaction.response.send_message(
                "❌ No tienes permisos.",
                ephemeral=True
            )

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute("""
                SELECT id, moderator_id, reason, created_at
                FROM warnings
                WHERE guild_id = ? AND user_id = ?
                ORDER BY id DESC
            """, (
                interaction.guild.id,
                usuario.id
            ))

            warns = await cursor.fetchall()

        if not warns:
            return await interaction.response.send_message(
                f"✅ {usuario.mention} no tiene warnings."
            )

        embed = discord.Embed(
            title=f"⚠️ Warnings de {usuario.display_name}",
            color=discord.Color.orange()
        )

        desc = ""

        for warn_id, mod_id, reason, created_at in warns:

            # HAMMER TIME (Discord timestamp)
            try:
                import datetime
                dt = datetime.datetime.strptime(
                    created_at, "%Y-%m-%d %H:%M:%S"
                )
                ts = int(dt.timestamp())
            except:
                ts = 0

            desc += (
                f"**Warn #{warn_id}**\n"
                f"👮 <@{mod_id}>\n"
                f"✉ {reason}\n"
                f"📅 <t:{ts}:F>\n\n"
            )

        embed.description = desc

        await interaction.response.send_message(embed=embed)

    # -------------------------
    # /unwarn
    # -------------------------
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="unwarn",
        description="Eliminar una advertencia"
    )
    async def unwarn(
        self,
        interaction: discord.Interaction,
        warn_id: int
    ):

        if not await is_mod(interaction.user):
            return await interaction.response.send_message(
                "❌ No tienes permisos.",
                ephemeral=True
            )

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute("""
                SELECT user_id, reason
                FROM warnings
                WHERE id = ?
            """, (warn_id,))

            data = await cursor.fetchone()

            if not data:
                return await interaction.response.send_message(
                    "❌ Warn no encontrado.",
                    ephemeral=True
                )

            user_id, reason = data

            await db.execute("""
                DELETE FROM warnings
                WHERE id = ?
            """, (warn_id,))

            await db.execute("""
                INSERT INTO punishments (
                    guild_id, user_id, moderator_id, action, reason
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                interaction.guild.id,
                user_id,
                interaction.user.id,
                "UNWARN",
                f"Warn #{warn_id} eliminado"
            ))

            await db.commit()

        embed = discord.Embed(
            title="🗑️ UNWARN",
            color=discord.Color.green()
        )

        embed.description = (
            f"Warn eliminado: #{warn_id}\n"
            f"Moderador: {interaction.user.mention}"
        )

        await send_log(interaction.guild, embed)

        await interaction.response.send_message(
            f"✅ Warn #{warn_id} eliminado."
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
