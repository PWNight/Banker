import disnake as discord
import shortuuid
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
import random
from api.server import base, main

class StaffCMD(commands.Cog):
    def __init__(self, client):
        self.client = client

                
def setup(client):
    client.add_cog(StaffCMD(client))