import aiosqlite
import discord

DB_NAME = "database.db"


async def get_guild_config(guild_id: int):

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
            (guild_id,)
        )

        return await cursor.fetchone()


async def send_log(
    guild: discord.Guild,
    embed: discord.Embed
):

    data = await get_guild_config(
        guild.id
    )

    if not data:
        return

    logs_channel = data[0]

    if not logs_channel:
        return

    channel = guild.get_channel(
        logs_channel
    )

    if channel:
        await channel.send(
            embed=embed
        )


async def send_punishment(
    guild: discord.Guild,
    content: str,
    embed: discord.Embed
):

    data = await get_guild_config(
        guild.id
    )

    if not data:
        return

    punishments_channel = data[1]

    if not punishments_channel:
        return

    channel = guild.get_channel(
        punishments_channel
    )

    if channel:
        await channel.send(
            content=content,
            embed=embed
        )


async def send_dm(
    member: discord.Member,
    embed: discord.Embed
):

    try:
        await member.send(
            embed=embed
        )
    except:
        pass

async def get_mod_role(guild_id: int):

    data = await get_guild_config(
        guild_id
    )

    if not data:
        return None

    return data[2]
