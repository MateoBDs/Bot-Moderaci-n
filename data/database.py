import aiosqlite

DB_NAME = "database.db"

async def init_db():
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute("""
    CREATE TABLE IF NOT EXISTS guild_config(
        guild_id INTEGER PRIMARY KEY,
        logs_channel INTEGER,
        punishments_channel INTEGER,
        mod_role INTEGER
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS warnings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        user_id INTEGER,
        moderator_id INTEGER,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS mutes(
        user_id INTEGER,
        guild_id INTEGER,
        end_time INTEGER
    )
    """)

    await db.commit()
```
