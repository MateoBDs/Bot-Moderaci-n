import aiosqlite

DB_NAME = "data/database.db"


async def is_mod(member):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT mod_role
        FROM guild_config
        WHERE guild_id = ?
        """, (member.guild.id,))

        data = await cursor.fetchone()

    if not data or not data[0]:
        return False

    return any(r.id == data[0] for r in member.roles)
