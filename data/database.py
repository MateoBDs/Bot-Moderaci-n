import aiosqlite

import os

DB_NAME = os.path.join("data", "database.db")


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        # Configuración por servidor
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_config(
            guild_id INTEGER PRIMARY KEY,
            logs_channel INTEGER,
            punishments_channel INTEGER,
            mod_role INTEGER
        )
        """)

        # Warnings
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

        # Historial completo de sanciones
        await db.execute("""
        CREATE TABLE IF NOT EXISTS punishments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            action TEXT,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Mutes activos
        await db.execute("""
        CREATE TABLE IF NOT EXISTS mutes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            reason TEXT,
            start_time INTEGER,
            end_time INTEGER,
            active INTEGER DEFAULT 1
        )
        """)

        # Roles guardados para restaurar tras un mute
        await db.execute("""
        CREATE TABLE IF NOT EXISTS mute_roles(
            guild_id INTEGER,
            user_id INTEGER,
            roles TEXT
        )
        """)

        await db.commit()
