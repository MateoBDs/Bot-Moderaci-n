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

        # PUBLICO
        public = discord.Embed(
            description=f"""# ⚠️ WARN ⚠️
🠺 🧑Usuario: {user.name}
🠺 💻Moderador: {interaction.user.mention}
🠺 ✉Razón: {reason}

-# BDcell © 2026 | Moderación""",
            color=discord.Color.orange()
        )

        await interaction.channel.send(
            content=f"{user.mention} <@&1523282618408501358>",
            embed=public
        )

        # SANCTIONS LOG
        punish = discord.Embed(
            title="⚠ SANCIÓN",
            description=f"""
👤 {user.mention}
👮 {interaction.user.mention}
✉ {reason}
""",
            color=discord.Color.red()
        )

        await send_punishment(interaction.guild, punish)

        # LOGS
        log = discord.Embed(
            title="📋 WARN LOG",
            description=f"""
User: {user} ({user.id})
Mod: {interaction.user}
Reason: {reason}
""",
            color=discord.Color.dark_orange()
        )

        await send_log(interaction.guild, log)

        # DM
        try:
            dm = discord.Embed(
                title="⚠ Warn recibido",
                description=f"Servidor: {interaction.guild.name}\nRazón: {reason}",
                color=discord.Color.red()
            )
            await user.send(embed=dm)
        except:
            pass

        await interaction.followup.send("✅ Warn aplicado")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
