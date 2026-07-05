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

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# ERROR HANDLER GLOBAL
# =========================
@bot.tree.error
async def on_app_command_error(interaction, error):
    print("❌ ERROR APP COMMAND:")
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

            print(f"✅ {len(synced)} comandos sync en {guild_id}")

        except Exception as e:
            print(f"❌ Sync error {guild_id}: {e}")


# =========================
# LOAD COGS
# =========================
async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"✅ Cog: {file}")
            except Exception as e:
                print(f"❌ Cog error {file}: {e}")


# =========================
# MAIN
# =========================
async def main():

    os.makedirs("data", exist_ok=True)

    await init_db()

    async with bot:

        await load_cogs()

        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
