import disnake as discord
import traceback
from datetime import datetime
from disnake.ext import commands
from configs import config
from api.server import main


class Error(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_slash_command_error(self,inter, exception):
        if isinstance(exception, commands.MissingRole):
            await inter.send("<:minecraft_deny:1080779495386140684> Чтобы использовать команду нужна роль <@&1197579125037207572>",ephemeral=True)
        elif isinstance(exception, commands.CommandOnCooldown):
            await inter.send("<:minecraft_deny:1080779495386140684> Притормозите! Попробуйте использовать команду чуть позже",ephemeral=True)
        else:
            logschannel = self.client.get_channel(config.logserrors)
            responce_embed = discord.Embed(title=f'Критическая ошибка при выполнении команды /{inter.data.name}', color=0xE36565)
            responce_embed.description = f"Отдел разработки уже получил уведомление о неправильной работе команды и в ближайшее время восстановит работу команды."
            responce_embed.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            responce_embed.timestamp = datetime.now()
            await inter.send(embed = responce_embed, ephemeral = True)

            system_embed = discord.Embed(title=f'Критическая ошибка при выполнении команды /{inter.data.name}', color=0xE36565)
            system_embed.description = f"\n\nСообщение ошибки: {traceback.format_exception(exception)}"
            system_embed.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            system_embed.timestamp = datetime.now()
            await logschannel.send(embed = system_embed)
         
def setup(client):
    client.add_cog(Error(client))