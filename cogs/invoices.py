import datetime
import disnake as discord
from datetime import timezone, timedelta
from disnake.ext import commands, tasks
from api import base
from api import main
from api import webhook
import random2

class Invoices(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f"за штрафами"))
        self.invoices_check.start()

    @tasks.loop(minutes = 5)
    async def invoices_check(self):
        invoices_mass = base.request_all(f"SELECT * FROM invoices WHERE status NOT IN ('Оплачен','Отменён')")
        for invoice in invoices_mass:
            status = invoice['status']
            curr_date = datetime.datetime.now()
            due_date = invoice['due_date']
            if(curr_date > due_date):
                if(status == 'Не оплачен'):
                    await Invoices.notify(self,due_date,invoice)
                elif(status == 'Просрочен'):
                    await Invoices.twice_notify(self,due_date,invoice)
                        
    async def notify(self,date,invoice):
        #calc new due_date for invoice
        new_date = date + datetime.timedelta(days=3)
        due_date = datetime.datetime.strptime(str(new_date), '%Y-%m-%d %H:%M:%S')
        
        #get invoice info
        invoice_id = invoice['id']
        invoice_user = await self.client.fetch_user(int(invoice['for_userid']))
        invoice_author = await self.client.fetch_user(int(invoice['from_userid']))
        amount = invoice['amount']
        type = invoice['type']

        #update invoice status
        base.send(f"UPDATE `invoices` SET `status` = 'Просрочен', due_date = '{due_date}' WHERE id = '{invoice_id}'")

        #gen msg and send
        logs_message = discord.Embed(description=f"### Счёт `{invoice_id}` игрока {invoice_user.mention} просрочен \nТип счёта: `{type}` \nСумма счёта: `{amount}` алмазов \nСчёт выставил {invoice_author.mention} \n\nСчёт должен был быть оплачен до ~~`{date}`~~ -> `{new_date}`.",color=0x80d8ed)
        logs_message.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await webhook.logsSend(logs_message)

        responce_pm = discord.Embed(description=f"### Выставленный вам счёт `{invoice_id}` просрочен \nТип счёта: `{type}` \nСумма счёта: `{amount}` алмазов \nСчёт выставил {invoice_author.mention} \n\nСчёт должен был быть оплачен до ~~`{date}`~~ -> `{new_date}`.",color=0x80d8ed)
        responce_pm.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await invoice_user.send(embed=responce_pm)

    async def twice_notify(self,date,invoice):
        invoice_id = invoice['id']
        invoice_user = await self.client.fetch_user(int(invoice['for_userid']))
        invoice_author = await self.client.fetch_user(int(invoice['from_userid']))
        amount = invoice['amount']
        type = invoice['type']

        #update invoice status
        base.send(f"UPDATE `invoices` SET `status` = 'Повторно просрочен' WHERE id = '{invoice_id}'")

        #gen msg and send
        logs_message = discord.Embed(description=f"### Счёт `{invoice_id}` игрока {invoice_user.mention} повторно просрочен \nТип счёта: `{type}` \nСумма счёта: `{amount}` алмазов \nСчёт оформил {invoice_author.mention} \n\nСчёт должен был быть оплачен до `{date}`",color=0x80d8ed)
        logs_message.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await webhook.logsSend(logs_message)

        responce_pm = discord.Embed(description=f"### Ваш счёт `{invoice_id}` повторно просрочен \nТип счёта: `{type}` \nСумма счёта: `{amount}` алмазов \nСчёт оформил {invoice_author.mention} \n\nСчёт должен был быть оплачен до `{date}`",color=0x80d8ed)
        responce_pm.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await invoice_user.send(embed=responce_pm)
    
def setup(client):
    client.add_cog(Invoices(client))