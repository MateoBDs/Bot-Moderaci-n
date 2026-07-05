import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands

from utils.permissions import is_mod
from utils.logs import (
    send_log,
    send_punishment,
    send_dm
)

DB_NAME = "database.db"
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
    async def ping(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "🏓 Pong!"
        )

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="warn",
        description="Advierte a un usuario"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str
    ):

        if not await is_mod(
            interaction.user
        ):
            await interaction.response.send_message(
                "❌ No tienes permisos.",
                ephemeral=True
            )
            return

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute(
                """
                INSERT INTO warnings(
                    guild_id,
                    user_id,
                    moderator_id,
                    reason
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    interaction.guild.id,
                    usuario.id,
                    interaction.user.id,
                    razon
                )
            )

            await db.execute(
                """
                INSERT INTO punishments(
                    guild_id,
                    user_id,
                    moderator_id,
                    action,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    interaction.guild.id,
                    usuario.id,
                    interaction.user.id,
                    "WARN",
                    razon
                )
            )

            await db.commit()

        punishment_embed = discord.Embed(
            title="⚠️ WARN ⚠️",
            color=discord.Color.orange()
        )

        punishment_embed.description = (
            f"🠺 🧑 **Usuario:** {usuario.display_name}\n"
            f"🠺 💻 **Moderador:** {interaction.user.mention}\n"
            f"🠺 ✉ **Razón:** {razon}\n\n"
            f"> Si crees que tu sanción fue injusta, puedes abrir ticket en <#1522869806540259350>.\n\n"
            f"-# BDcell © 2026 | Moderación"
        )

        await send_punishment(
            interaction.guild,
            f"<@&1523282618408501358> {usuario.mention}",
            punishment_embed
        )

        dm_embed = discord.Embed(
            title="⚠️ Has recibido una advertencia",
            color=discord.Color.orange()
        )

        dm_embed.description = (
            f"Servidor: **{interaction.guild.name}**\n"
            f"Moderador: {interaction.user}\n"
            f"Razón: {razon}"
        )

        await send_dm(
            usuario,
            dm_embed
        )

        log_embed = discord.Embed(
            title="📋 Nuevo Warn",
            color=discord.Color.orange()
        )

        log_embed.add_field(
            name="Usuario",
            value=f"{usuario} ({usuario.id})",
            inline=False
        )

        log_embed.add_field(
            name="Moderador",
            value=f"{interaction.user} ({interaction.user.id})",
            inline=False
        )

        log_embed.add_field(
            name="Razón",
            value=razon,
            inline=False
        )

        await send_log(
            interaction.guild,
            log_embed
        )

        await interaction.response.send_message(
            f"✅ Advertencia enviada a {usuario.mention}"
        )

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="warnings",
        description="Ver advertencias de un usuario"
    )
    async def warnings(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        if not await is_mod(
            interaction.user
        ):
            await interaction.response.send_message(
                "❌ No tienes permisos.",
                ephemeral=True
            )
            return

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute(
                """
                SELECT
                    moderator_id,
                    reason,
                    created_at
                FROM warnings
                WHERE guild_id = ?
                AND user_id = ?
                ORDER BY id DESC
                LIMIT 20
                """,
                (
                    interaction.guild.id,
                    usuario.id
                )
            )

            warns = await cursor.fetchall()

        if not warns:

            await interaction.response.send_message(
                f"✅ {usuario.mention} no tiene advertencias."
            )
            return

        embed = discord.Embed(
            title=f"⚠️ Advertencias de {usuario}",
            color=discord.Color.orange()
        )

        description = ""

        for i, warn in enumerate(
            warns,
            start=1
        ):

            moderator_id, reason, created_at = warn

            description += (
                f"**#{i}**\n"
                f"👮 <@{moderator_id}>\n"
                f"✉ {reason}\n"
                f"📅 {created_at}\n\n"
            )

        embed.description = description

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Moderation(bot)
    )
