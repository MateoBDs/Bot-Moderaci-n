import aiosqlite

DB_NAME = "database.db"


async def is_mod(member):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT mod_role
            FROM guild_config
            WHERE guild_id = ?
            """,
            (member.guild.id,)
        )

        data = await cursor.fetchone()

    if not data:
        return False

    mod_role = data[0]

    if not mod_role:
        return False

    return any(role.id == mod_role for role in member.roles)
