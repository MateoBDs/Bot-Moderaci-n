from discord.ext import commands
from discord import app_commands
import discord

class Moderation(commands.Cog):

```
def __init__(self, bot):
    self.bot = bot

@app_commands.command(
    name="ping",
    description="Comprueba si el bot funciona."
)
async def ping(self, interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🏓 Pong! {round(self.bot.latency * 1000)}ms"
    )
```

async def setup(bot):
await bot.add_cog(Moderation(bot))
