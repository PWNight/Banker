import disnake as discord
from disnake.ext import commands
from os import listdir
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
    
# ? -----------------
# ? | UTIL CATEGORY |
# ? -----------------

client.version = config.version
client.config = config

# ? --------------------
# ? | BOT REGISTRATION |
# ? --------------------

client.run(config.token)