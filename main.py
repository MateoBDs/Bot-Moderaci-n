import os
import asyncio
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
    print(f"✅ Conectado como {bot.user} ({bot.user.id})")

    for guild_id in GUILDS:
        guild = discord.Object(id=guild_id)

        try:
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ {len(synced)} comandos sincronizados en {guild_id}")

        except Exception as e:
            print(f"❌ Error sync {guild_id}: {e}")


async def load_cogs():

    for filename in os.listdir("./cogs"):

        if filename.endswith(".py"):

            extension = f"cogs.{filename[:-3]}"

            try:
                await bot.load_extension(extension)
                print(f"✅ Cog cargado: {extension}")

            except Exception as e:
                print(f"❌ Error cargando {extension}: {e}")


async def main():

    os.makedirs("data", exist_ok=True)  # 👈 esto va AQUÍ pero bien indentado

    await init_db()

    async with bot:

        await load_cogs()

        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
