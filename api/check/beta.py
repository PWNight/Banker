import disnake as discord
import json
from disnake.ext import commands


def beta():
    def wrapper(ctx):
        with open('data/access/beta.json') as f:
            beta = json.load(f)
        if ctx.author.id in beta:
            return True
        raise commands.MissingPermissions('Данная команда доступна лишь для Бета-тестеров')
    return commands.check(wrapper)