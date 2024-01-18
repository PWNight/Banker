from datetime import datetime
import disnake as discord
from disnake.ext import commands, tasks
from api.server import base
import datetime


class Error(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_slash_command_error(self,inter, error):
        if isinstance(error, commands.MissingRole):
            await inter.send("<:minecraft_deny:1080779495386140684> Чтобы использовать команду нужна роль <@&1197579125037207572>",ephemeral=True)
        if isinstance(error, commands.CommandOnCooldown):
            await inter.send("<:minecraft_deny:1080779495386140684> Притормозите! Попробуйте использовать команду чуть позже",ephemeral=True)
         
def setup(client):
    client.add_cog(Error(client))