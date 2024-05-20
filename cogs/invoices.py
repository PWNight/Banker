from datetime import datetime
import disnake as discord
from disnake.ext import commands, tasks
from api.server import base, main

class Invoices(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f"за штрафами"))
        self.status_task.start()

    @tasks.loop(hours = 1)
    async def status_task(self):
            dates_mass = base.request_all(f"SELECT due_date FROM invoices WHERE status = 'Не оплачен'")
            for date in dates_mass:
                date = datetime.datetime.strptime(str(date['date_give']), '%Y-%m-%d %H:%M:%S')
                if (datetime.datetime.now() - date) > datetime.timedelta(minutes=1):
                    invoice = base.request_one(f"SELECT * FROM invoices WHERE due_date = '{date}'")
                    await Invoices.notify(self,date,invoice)
    async def notify(self,date,invoice):
        #calc new due_date for invoice
        new_date = date + datetime.timedelta(days=3)
        
        logchannel = self.client.get_channel(1111753012441006201)
        invoice_id = invoice['id']
        invoice_user = await self.client.fetch_user(int(invoice['for_userid']))
        invoice_author = await self.client.fetch_user(int(invoice['from_userid']))
        amount = invoice['amount']
        type = invoice['type']

        #update invoice status
        base.send(f"UPDATE `invoices` SET `status` = 'Просрочен' WHERE id = '{invoice_id}'")

        #gen msg and send
        responce_chnl = discord.Embed(description=f"### Счёт `{invoice_id}` игрока {invoice_user.mention} просрочен \nТип счёта: `{type}` \nСумма счёта: `{amount}` алмазов \nСчёт оформил {invoice_author.mention} \n\nСчёт должен был быть оплачен до `{date}` \nОплата счёта была перенесена до `{new_date}`, после повторной неуплаты будет заведено судебное дело.",color=0xF7B060)
        responce_chnl.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await logchannel.send(embed=responce_chnl)

        responce_pm = discord.Embed(description=f"### Ваш счёт `{invoice_id}` просрочен \nТип счёта: `{type}` \nСумма счёта: `{amount}` алмазов \nСчёт оформил {invoice_author.mention} \n\nСчёт должен был быть оплачен до `{date}` \nОплата счёта была перенесена до `{new_date}`, после повторной неуплаты будет заведено судебное дело.",color=0xF7B060)
        responce_pm.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await invoice_user.send(embed=responce_pm)
         
def setup(client):
    client.add_cog(Invoices(client))