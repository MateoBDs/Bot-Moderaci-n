import os
import asyncio
import discord
import traceback

from discord.ext import commands
from dotenv import load_dotenv

from data.database import init_db
from config import GUILDS

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# ERROR HANDLER GLOBAL
# =========================
@bot.tree.error
async def on_app_command_error(interaction, error):
    print("❌ ERROR EN APP COMMAND:")
    traceback.print_exception(type(error), error, error.__traceback__)


# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user} ({bot.user.id})")

    for guild_id in GUILDS:
        try:
            guild = discord.Object(id=guild_id)

            synced = await bot.tree.sync(guild=guild)

            print(f"✅ {len(synced)} comandos sincronizados en {guild_id}")

        except Exception as e:
            print(f"❌ Error sync {guild_id}: {e}")


# =========================
# LOAD COGS
# =========================
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Cog cargado: cogs.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Error cargando cog {filename}: {e}")


# =========================
# START BOT
# =========================
async def main():

    os.makedirs("data", exist_ok=True)

    await init_db()

    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
