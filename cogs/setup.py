import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands

DB_NAME = "database.db"

GUILD_ID = 1522869805462589593


class Setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def ensure_guild(self, guild_id: int):

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute(
                "SELECT guild_id FROM guild_config WHERE guild_id = ?",
                (guild_id,)
            )

            data = await cursor.fetchone()

            if not data:

                await db.execute(
                    """
                    INSERT INTO guild_config(
                        guild_id,
                        logs_channel,
                        punishments_channel,
                        mod_role
                    )
                    VALUES (?, NULL, NULL, NULL)
                    """,
                    (guild_id,)
                )

                await db.commit()

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="setup_logs",
        description="Configura el canal de logs."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_logs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        await self.ensure_guild(
            interaction.guild.id
        )

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute(
                """
                UPDATE guild_config
                SET logs_channel = ?
                WHERE guild_id = ?
                """,
                (
                    canal.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        await interaction.response.send_message(
            f"✅ Canal de logs configurado: {canal.mention}"
        )

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="setup_sanciones",
        description="Configura el canal de sanciones."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_sanciones(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        await self.ensure_guild(
            interaction.guild.id
        )

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute(
                """
                UPDATE guild_config
                SET punishments_channel = ?
                WHERE guild_id = ?
                """,
                (
                    canal.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        await interaction.response.send_message(
            f"✅ Canal de sanciones configurado: {canal.mention}"
        )

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="setup_modrole",
        description="Configura el rol de moderación."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_modrole(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):

        await self.ensure_guild(
            interaction.guild.id
        )

        async with aiosqlite.connect(DB_NAME) as db:

            await db.execute(
                """
                UPDATE guild_config
                SET mod_role = ?
                WHERE guild_id = ?
                """,
                (
                    rol.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        await interaction.response.send_message(
            f"✅ Rol moderador configurado: {rol.mention}"
        )

    @app_commands.guilds(
        discord.Object(id=GUILD_ID)
    )
    @app_commands.command(
        name="setup_ver",
        description="Ver configuración actual."
    )
    async def setup_ver(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DB_NAME) as db:

            cursor = await db.execute(
                """
                SELECT
                    logs_channel,
                    punishments_channel,
                    mod_role
                FROM guild_config
                WHERE guild_id = ?
                """,
                (
                    interaction.guild.id,
                )
            )

            data = await cursor.fetchone()

        if not data:

            await interaction.response.send_message(
                "❌ No hay configuración."
            )
            return

        logs, sanciones, mod_role = data

        embed = discord.Embed(
            title="⚙️ Configuración",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Logs",
            value=f"<#{logs}>" if logs else "No configurado",
            inline=False
        )

        embed.add_field(
            name="Sanciones",
            value=f"<#{sanciones}>" if sanciones else "No configurado",
            inline=False
        )

        embed.add_field(
            name="Rol Moderador",
            value=f"<@&{mod_role}>" if mod_role else "No configurado",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Setup(bot)
    )
