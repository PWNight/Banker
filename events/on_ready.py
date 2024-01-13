from datetime import datetime
import disnake as discord
from disnake.ext import commands, tasks
from api.server import base
import datetime


class OnReady(commands.Cog):
    def __init__(self, client):
        self.client = client
    async def expired_notify(date):
        pass
    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.dnd,activity = discord.Activity(type = discord.ActivityType.watching, name = f"за разработкой"))
        #self.status_task.start()

    #@tasks.loop(minutes = 1)
    #async def status_task(self):
    #        dates_mass = base.get_active_fine_dates()
    #        for date in dates_mass:
    #            date = datetime.datetime.strptime(str(date['date_give']), '%Y-%m-%d %H:%M:%S')
    #            print(date)
    #            if (datetime.datetime.now() - date) > datetime.timedelta(minutes=2):
    #                await fines.Fines.notify(self,date)
    #    #await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"за нарушителями"))
    #    #await self.client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"за тех.работами")
         
def setup(client):
    client.add_cog(OnReady(client))