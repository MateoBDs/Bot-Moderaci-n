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


@bot.tree.error
async def on_app_command_error(interaction, error):
    print("❌ ERROR:")
    traceback.print_exception(type(error), error, error.__traceback__)


@bot.event
async def on_ready():
    print(f"✅ Logged as {bot.user}")

    for guild_id in GUILDS:
        try:
            synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
            print(f"✅ Sync {len(synced)} cmds {guild_id}")
        except Exception as e:
            print("SYNC ERROR:", e)


async def load_cogs():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{f[:-3]}")
                print("Cog:", f)
            except Exception as e:
                print("Cog error:", e)


async def main():
    await init_db()

    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
