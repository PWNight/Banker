import sqlite3
import psutil
import disnake as discord
from disnake.ext import commands
from api.check import utils
from os import listdir

from api.server import main
from configs import config

# ? ------------------------
# ? | SETUP DISCORD CLIENT |
# ? ------------------------

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.messages = True

client = commands.Bot(
    command_prefix = f'{config.prefix}',
    help_command = None,
    intents = discord.Intents.all()
)

# ? ----------------
# ? | LOADING COGS |
# ? ----------------

for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


for filename in listdir('./events/'):
    if filename.endswith('.py'):
        client.load_extension(f'events.{filename[:-3]}')

# ? --------------------
# ? | BOT DEV CATEGORY |
# ? --------------------

@client.command()
@utils.developer()
async def reload(ctx, extension):
    client.reload_extension(f"cogs.{extension}")
    await ctx.reply(embed = main.done(ctx.guild, f"Модуль `{extension}` был перезагружен"))
    
# * ----------------

@client.command()
@utils.developer()
async def ereload(ctx, extension):
    client.reload_extension(f"events.{extension}")
    await ctx.reply(embed = main.done(ctx.guild, f"Событие `{extension}` было перезагружено"))
    
# ? -----------------
# ? | UTIL CATEGORY |
# ? -----------------

client.version = config.version
client.config = config

# ? --------------------
# ? | BOT REGISTRATION |
# ? --------------------

client.run(config.token)