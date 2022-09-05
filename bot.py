import nextcord
from nextcord.ext import commands

from module_analyze import ModuleAnalyze
from secrets import key

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', description = "A Discord bot that archives entire servers, storing every message in a SQLite database for easy querying.", intents = intents)
client = nextcord.Client()


@bot.event
async def on_ready():
    print('Logged in as', bot.user.name, "(" + str(bot.user.id) + ")")
    print('------')


bot.add_cog(ModuleAnalyze(bot))

bot.run(key)
