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
        self.bankday_check.start()
    @tasks.loop(hours=24)
    async def bankday_check(self):
        curr_date = datetime.datetime.now()
        curr_day = curr_date.day
        if(curr_day == 1):
            cards_mass = base.request_all(f"SELECT id, owner_id FROM cards")
            for card in cards_mass:
                await Invoices.commision_invoice(self,card)
            logs_message = discord.Embed(description=f"### Выставлено {len(cards_mass)} счетов на оплату банковской комиссии \nНаступило 1-е число месяца, поэтому банковская система в автоматическом режиме выставила счета за обслуживание карт каждому клиенту.",color=0x80d8ed)
            logs_message.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
            await webhook.logsSend(logs_message)
    @tasks.loop(hours = 1)
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

    async def commision_invoice(self,card):
        #func gen card and validate card id (example: 0011)
        def gen_id():
            random_int = random2.randint(1,999999)
            random_int = str(random_int)
            if len(random_int) == 1:
                random_int = '00000' + random_int
            if len(random_int) == 2:
                random_int = '0000' + random_int
            if len(random_int) == 3:
                random_int = '000' + random_int
            if len(random_int) == 4:
                random_int = '00' + random_int
            if len(random_int) == 5:
                random_int = '0' + random_int
            return random_int
        
        async def validate_id():
            invoice_id = gen_id()
            print(invoice_id)
            is_card_exists = base.request_one(f"SELECT * FROM `invoices` WHERE id = '{invoice_id}'")
            if is_card_exists != None:
                validate_id()
            else:
                return invoice_id
            
        #calc new due_date for invoice
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        curr_date = datetime.datetime.now(tzinfo)
        new_date = curr_date + datetime.timedelta(days=30)
        new_date = str(new_date).split('.')
        new_date = new_date[0]
        new_date = datetime.datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S')
        
        invoice_id = await validate_id()
        invoice_userid = card['owner_id']
        invoice_user = await self.client.fetch_user(int(invoice_userid))
        invoice_authorid = 1195315985532604506
        amount = 10
        type = 'Банковская комиссия'

        #update invoice status
        base.send(f"INSERT INTO invoices(id,type,for_userid,from_userid,to_userid,amount,due_date,status) VALUES('{invoice_id}','{type}','{invoice_userid}','{invoice_authorid}','1195315985532604506',{amount},'{new_date}','Не оплачен')")

        #gen msg and send
        responce_pm = discord.Embed(description=f"### Вам выставлен счёт `{invoice_id}` суммов в {amount} алмазов на оплату банковской комиссии \nКаждое 1-е число месяца банковская система автоматически выставляет счета за обслуживание карт каждому клиенту. \nОплатить счёт можно по команде `/оплатить-счёт [номер-счёта]`",color=0x80d8ed)
        responce_pm.set_footer(text=f'{main.copyright()} | ID: {invoice_id}',icon_url=f'https://cdn.discordapp.com/emojis/1105878293187678208.webp?size=96&quality=lossless')
        await invoice_user.send(embed=responce_pm)
         
def setup(client):
    client.add_cog(Invoices(client))