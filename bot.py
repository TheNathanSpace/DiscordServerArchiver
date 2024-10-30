import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

import nextcord
from nextcord.ext import commands

from module_analyze import CogArchive
from secrets import key

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   description="A Discord bot that archives entire servers, storing every message in a SQLite database for easy querying.",
                   intents=intents)
client = nextcord.Client()


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")


bot.add_cog(CogArchive(bot))

bot.run(key)
