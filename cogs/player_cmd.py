import disnake as discord
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
from api.server import base, main
from configs import config

class PlayerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="перевести", description="💵 Переводит алмазы на указанную карту", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_money(self, inter, card_id: str, sum: int):
        await inter.response.defer(ephemeral = True)
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'{config.deny} Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 5000):
            await inter.send(f'{config.deny} За раз можно перевести не более 5000 алмазов.',ephemeral=True)
            return
        
        #card id validation
        if(len(card_id) != 4):
            await inter.send(f'{config.deny} Неправильный номер карты. Пример номера: `0001`.',ephemeral=True)
            return
        try:
            int(card_id)
        except ValueError:
            await inter.send(f'{config.deny} Неправильный номер карты. Пример номера: `0001`.',ephemeral=True)
            return
        card_id = int(card_id)
        
        #get cards info by inter id and card id
        owner_card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {inter.author.id}")
        reciever_card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if owner_card_info == None:
            await inter.send(f'{config.deny} На ваше имя нету зарегистрированных карт, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        if reciever_card_info == None:
            await inter.send(f'{config.deny} Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        
        #check users id
        owner_id = owner_card_info['owner_id']
        reciever_id = reciever_card_info['owner_id']
        if(owner_id == reciever_id):
            await inter.send(f'{config.deny} Вы не можете перевести алмазы самому себе.',ephemeral=True)
            return
        
        logchannel = self.client.get_channel(config.logschannel)
        owner = await self.client.fetch_user(int(owner_id))
        owner_card_id = owner_card_info['id']
        reciever = await self.client.fetch_user(int(reciever_id))
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = str(datetime.datetime.now(tzinfo)).split('.')[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
        timestamp = f"<t:{timestamp}:f>"

        #get and calc new balance
        owner_balance = int(owner_card_info['balance'])
        reciever_balance = int(reciever_card_info['balance'])
        if owner_balance < sum:
            await inter.send(f'{config.deny} На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а снимается `{sum}` алмазов).',ephemeral=True)
            return
        owner_balance -= sum
        reciever_balance += sum
        
        #update balance in DB
        base.send(f"UPDATE `cards` SET `balance` = {owner_balance} WHERE id = {owner_card_id}")
        base.send(f"UPDATE `cards` SET `balance` = {reciever_balance} WHERE id = {card_id}")

        #gen and send responce
        await inter.send(f"{config.accept} 💸 Вы перевели {sum} алмазов на карту `FW-{card_id}`.",ephemeral=True)

        responce_chnl_system = discord.Embed(description=f"### 💸 Пользователь {owner.mention} перевёл пользователю {reciever.mention} {sum} алмазов \nКарта владельца: `FW-{owner_card_id}`. \nКарта получателя: `FW-{card_id}`. \n\nДата оформления транзакции: {timestamp}.",color=0xEFAF6F)
        responce_chnl_system.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl_system)

        responce_owner_pm = discord.Embed(description=f"### Вы перевели {sum} алмазов на карту `FW-{card_id}` \nДата оформления транзакции: {timestamp}.",color=0xEFAF6F)
        responce_owner_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_owner_pm)

        responce_reciever_pm = discord.Embed(description=f"### Вы получили {sum} алмазов на карту `FW-{card_id}` \nПеревод поступил от {owner.mention} (`FW-{owner_card_id}`) \nДата оформления транзакции: {timestamp}.",color=0xEFAF6F)
        responce_reciever_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await reciever.send(embed=responce_reciever_pm)
        
    @commands.slash_command(name="оплатить-счёт", description="💵 Оплачивает указанный счёт", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.cooldown(1,10, commands.BucketType.user)
    async def pay_invoice(self, inter, invoice_id = str):
        await inter.response.defer(ephemeral = True)
        #card id validation
        if(len(invoice_id) != 6):
            await inter.send(f'{config.deny} Неправильный номер счёта. Пример номера: `000001`.',ephemeral=True)
            return
        try:
            int(invoice_id)
        except ValueError:
            await inter.send(f'{config.deny} Неправильный номер счёта. Пример номера: `000001`.',ephemeral=True)
            return
        invoice_id = invoice_id

        #get owner card info
        owner_inter = inter.author
        owner_card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {owner_inter.id}")
        if owner_card_info == None:
            await inter.send(f'{config.deny} Вы не обладаете никакими картами, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return

        #check is invoice exists
        #invoice = base.request_one(f"SELECT * FROM `invoices` WHERE for_userid = '{inter.author.id}' AND id = '{invoice_id}' AND status != 'Оплачен'")
        invoice = base.request_one(f"SELECT * FROM `invoices` WHERE id = '{invoice_id}' AND status != 'Оплачен'")
        if invoice == None:
            #invoice = base.request_one(f"SELECT * FROM `invoices` WHERE id = '{invoice_id}' AND status != 'Оплачен'")
            #if invoice == None:
            #    await inter.send(f'{config.deny} Указанный вами счёт `{invoice_id}` не существует.',ephemeral=True)
            #    return
            await inter.send(f'{config.deny} Указанный вами счёт `{invoice_id}` зарегистрирован не на ваш аккаунт.',ephemeral=True)
            return
        
        #get invoice info
        owner = await self.client.fetch_user(int(invoice['for_userid']))
        amount = int(invoice['amount'])
        type = invoice['type']
        invoice_author = await self.client.fetch_user(int(invoice['from_userid']))

        #get card id, balance and calc new balance
        owner_card_id = int(owner_card_info['id'])
        owner_balance = int(owner_card_info['balance'])
        if owner_balance < amount:
            await inter.send(f"{config.deny} На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а для оплаты нужно `{amount}` алмазов).",ephemeral=True)
            return
        owner_balance -= amount

        #update balance and invoice status
        base.send(f"UPDATE `cards` SET `balance` = '{owner_balance}' WHERE id = '{owner_card_id}'")
        card1_info = base.request_one(f"SELECT balance FROM `cards` WHERE id = 0001")
        balance = int(card1_info['balance'])
        balance += amount
        base.send(f"UPDATE `cards` SET `balance` = '{balance}' WHERE id = 0001")
        base.send(f"UPDATE `invoices` SET `status`= 'Оплачен' WHERE id = '{invoice_id}'")

        logchannel = self.client.get_channel(int(config.logschannel))
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = str(datetime.datetime.now(tzinfo)).split('.')[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
        timestamp = f"<t:{timestamp}:f>"

        #remove fine if type == fine
        if(type == 'Штраф'):
            base.send(f"UPDATE fines SET status = 'Оплачен' WHERE invoice_id = '{invoice_id}'")
            fine = base.request_one(f"SELECT id FROM fines WHERE invoice_id = '{invoice_id}'")
            fine_id = fine['id']
            notifychnl = self.client.get_channel(int(config.notifychnl))
            
            if(owner != owner_inter):
                responce_chnl = discord.Embed(description=f"### 💵 Пользователь {owner_inter.mention} оплатил штраф `{fine_id}` игрока {owner.mention}",color=0x80d8ed)
                responce_pm = discord.Embed(description=f"### Ваш штраф `{fine_id}` успешно оплачен игроком {owner_inter.mention} \nПриятной игры!",color=0x80d8ed)
            else:
                responce_chnl = discord.Embed(description=f"### 💵 Пользователь {owner.mention} оплатил штраф `{fine_id}`",color=0x80d8ed)
                responce_pm = discord.Embed(description=f"### Ваш штраф `{fine_id}` успешно оплачен \nПриятной игры!",color=0x80d8ed)
            responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await notifychnl.send(embed=responce_chnl)

            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await owner.send(embed=responce_pm)
        else:
            #gen and send responce
            if(owner != owner_inter):
                responce_chnl_system = discord.Embed(description=f"### 💵 Пользователь {owner_inter.mention} оплатил счёт `{invoice_id}` игрока {owner.mention} \nТип счёта: `{type}`\nСумма счёта: `{amount}` алмазов \n\nСчёт оформлен банкиром {invoice_author.mention} \nДата выполнения операции: {timestamp}.",color=0x80d8ed)
                responce_pm2 = discord.Embed(description=f"### Вас счёт `{invoice_id}` успешно оплачен \nТип счёта: `{type}`\nСумма счёта: `{amount}` алмазов \n\nСчёт оформлен банкиром {invoice_author.mention} \nДата выполнения операции: {timestamp}.",color=0x80d8ed)
            else:
                responce_chnl_system = discord.Embed(description=f"### 💵 Пользователь {owner_inter.mention} оплатил счёт `{invoice_id}` игрока {owner.mention} \nТип счёта: `{type}`\nСумма счёта: `{amount}` алмазов \n\nСчёт оформлен банкиром {invoice_author.mention} \nДата выполнения операции: {timestamp}.",color=0x80d8ed)
                responce_pm2 = discord.Embed(description=f"### Вас счёт `{invoice_id}` успешно оплачен \nТип счёта: `{type}`\nСумма счёта: `{amount}` алмазов \n\nСчёт оформлен банкиром {invoice_author.mention} \nДата выполнения операции: {timestamp}.",color=0x80d8ed)
            
            responce_chnl_system.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await logchannel.send(embed=responce_chnl_system)

            responce_pm2.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await owner.send(embed=responce_pm2)
        await inter.send(f"{config.accept} Счёт `{invoice_id}` успешно оплачен.",ephemeral=True)

    @commands.slash_command(name="баланс", description="💳 Показывает баланс вашей карты или указанного пользователя", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, inter, member: discord.Member = None):
        await inter.response.defer(ephemeral = True)
        guild = self.client.get_guild(inter.guild.id) 
        banker_role = discord.utils.get(guild.roles,id=config.banker_role)

        if member != None:
            if banker_role not in inter.author.roles:
                member = inter.author
                responce = discord.Embed(description=f"### Информация по вашим картам:",color=0x80d8ed)
                responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            else:
                responce = discord.Embed(description=f"### Информация по картам {member.mention}:",color=0x80d8ed)
                responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        if member == None:
            member = inter.author
            responce = discord.Embed(description=f"### Информация по вашим картам:",color=0x80d8ed)
            responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')

        #get card info by member id
        card_info = base.request_all(f"SELECT * FROM `cards` WHERE owner_id = {member.id}")
        if card_info == ():
            await inter.send(f'{config.deny} Не нашёл зарегистрированных карт на имя {member.mention}.',ephemeral=True)
            return
        
        #gen and send responce
        for x in card_info:
            card_id = x['id']
            card_balance = x['balance']
            card_opendate = x['date_open']
            banker = await self.client.fetch_user(int(x['banker_id']))
            responce.add_field(inline=False, name=f'Карта `FW-{card_id}`', value=f"Баланс: `{card_balance}`. \nОформлена банкиром {banker.mention}. \nДата оформления: `{card_opendate}`")

        await inter.send(embed=responce, ephemeral=True)
                
def setup(client):
    client.add_cog(PlayerCMD(client))