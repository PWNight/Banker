import disnake as discord
import traceback
from datetime import datetime
from disnake.ext import commands
from configs import config
from api import main


class Error(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_slash_command_error(self,inter, exception):
        embed = discord.Embed(
            description=f"<a:load:1256975206455447643> Произошла ошибка при выполнении команды, выясняю причину..",
            color=0x2f3136
        )
        await inter.send(embed = embed, ephemeral = True)

        if isinstance(exception, commands.MissingRole):
            embed.description = f"<:minecraft_deny:1080779495386140684> У вас нету доступа к данной команде."
            await inter.edit_original_response(embed = embed)
        elif isinstance(exception, commands.CommandOnCooldown):
            embed.description = f"<:minecraft_deny:1080779495386140684> Притормозите! Попробуйте использовать команду чуть позже."
            await inter.edit_original_response(embed = embed)
        else:
            logschannel = self.client.get_channel(config.logserrors)
            responce_embed = discord.Embed(
                description=f'## Неизвестная ошибка при выполнении команды /{inter.data.name} \nОтдел разработки уже получил уведомление о неправильной работе команды и в ближайшее время восстановит работу команды. \n\nПопробуйте использовать команду в любом другом канале Discord сервера.',
                color=0xE36565
            )
            responce_embed.set_footer(
                text=f'{main.copyright()}',
                icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&'
            )
            responce_embed.timestamp = datetime.now()
            await inter.edit_original_response(embed = responce_embed)

            system_embed = discord.Embed(
                description=f'## Неизвестная ошибка при выполнении команды /{inter.data.name} \nСообщение ошибки: {traceback.format_exception(exception)}',
                color=0xE36565
            )
            system_embed.set_footer(
                text=f'{main.copyright()}',
                icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&'
            )
            system_embed.timestamp = datetime.now()
            await logschannel.send(embed = system_embed)

def setup(client):
    client.add_cog(Error(client))