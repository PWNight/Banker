import disnake as discord
from disnake.ext import commands


class OnReady(commands.Cog):
    def __init__(self, client):
        self.client = client
    async def expired_notify(date):
        pass
    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.dnd,activity = discord.Activity(type = discord.ActivityType.watching, name = f"за разработкой"))
         
def setup(client):
    client.add_cog(OnReady(client))