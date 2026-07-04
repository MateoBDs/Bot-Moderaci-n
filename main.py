import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

from config import GUILDS
from data.database import init_db

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
command_prefix="!",
intents=intents
)

@bot.event
async def on_ready():

```
print(f"Conectado como {bot.user}")

for guild_id in GUILDS:

    guild = discord.Object(id=guild_id)

    bot.tree.copy_global_to(
        guild=guild
    )

    synced = await bot.tree.sync(
        guild=guild
    )

    print(
        f"{len(synced)} comandos sincronizados en {guild_id}"
    )
```

async def load_cogs():

```
await bot.load_extension(
    "cogs.moderation"
)
```

async def main():

```
await init_db()

async with bot:

    await load_cogs()

    await bot.start(TOKEN)
```

import asyncio
asyncio.run(main())
