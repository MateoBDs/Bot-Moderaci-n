import aiosqlite
import discord

DB_NAME = "data/database.db"


async def get_config(guild_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT logs_channel, punishments_channel
        FROM guild_config
        WHERE guild_id = ?
        """, (guild_id,))
        return await cursor.fetchone()


async def send_log(guild, embed):
    data = await get_config(guild.id)
    if not data or not data[0]:
        return

    channel = guild.get_channel(data[0])
    if channel:
        await channel.send(embed=embed)


async def send_punishment(guild, embed):
    data = await get_config(guild.id)
    if not data or not data[1]:
        return

    channel = guild.get_channel(data[1])
    if channel:
        await channel.send(embed=embed)
