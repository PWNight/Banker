import disnake as discord
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
from api.server import base, main
from configs import config

class PlayerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="перевести", description="💵 Переводит алмазы на указанную карту", test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_money(self, inter, card_id: str, sum: int):
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'{config.deny} Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 1000):
            await inter.send(f'{config.deny} За раз можно перевести не более 1000 алмазов.',ephemeral=True)
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
        date = datetime.datetime.now(tzinfo)
        done_date = date.strftime("%Y-%m-%d %H:%M")

        #get and calc new balance
        owner_balance = owner_card_info['balance']
        reciever_balance = reciever_card_info['balance']
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

        responce_chnl = discord.Embed(description=f"### 💸 Пользователь {owner.mention} перевёл пользователю {reciever.mention} {sum} алмазов \nКарта владельца: `FW-{owner_card_id}`. \nКарта получателя: `FW-{card_id}`. \n\nДата оформления транзакции: `{done_date}`.",color=0xEFAF6F)
        responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl)

        responce_pm = discord.Embed(description=f"### Вы перевели пользователю {reciever.mention} {sum} алмазов \nКарта владельца: `FW-{owner_card_id}`. \nКарта получателя: `FW-{card_id}`. \nДата оформления транзакции: `{done_date}`. \n\nЕсли алмазы были переведены не вами, немедленно сообщите об этом команде проекта.",color=0xEFAF6F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)
        
    @commands.slash_command(name="оплатить-счёт", description="💵 Оплачивает указанный счёт", test_guilds=[921483461016031263])
    @commands.cooldown(1,10, commands.BucketType.user)
    async def pay_invoice(self, inter, invoice_id = str):
        #card id validation
        if(len(invoice_id) != 6):
            await inter.send(f'{config.deny} Неправильный номер счёта. Пример номера: `000001`.',ephemeral=True)
            return
        try:
            int(invoice_id)
        except ValueError:
            await inter.send(f'{config.deny} Неправильный номер счёта. Пример номера: `000001`.',ephemeral=True)
            return
        
        #get owner and this card info
        owner = inter.author
        owner_card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {owner.id}")
        if owner_card_info == None:
            await inter.send(f'{config.deny} Вы не обладаете никакими картами, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        
        #check is invoice exists
        invoice = base.request_all(f"SELECT * FROM `invoices` WHERE for_userid = {inter.author.id} AND id = '{invoice_id}' AND status != 'Оплачен'")
        if invoice == ():
            invoice = base.request_all(f"SELECT * FROM `invoices` WHERE id = '{invoice_id}' AND status != 'Оплачен'")
            if invoice == ():
                await inter.send(f'{config.deny} Указанный вами счёт `{invoice_id}` не существует.',ephemeral=True)
                return
            await inter.send(f'{config.deny} Указанный вами счёт `{invoice_id}` зарегистрирован не на ваш аккаунт.',ephemeral=True)
            return
        
        #get invoice info
        amount = invoice['amount']
        type = invoice['type']
        invoice_author = await self.client.fetch_user(int(invoice['from_userid']))

        #get card id, balance and calc new balance
        owner_card_id = owner_card_info['id']
        owner_balance = owner_card_info['balance']
        if owner_balance < amount:
            await inter.send(f"{config.deny} На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а для оплаты нужно `{amount}` алмазов).",ephemeral=True)
            return
        owner_balance -= amount

        #update balance and invoice status
        base.send(f"UPDATE `cards` SET `balance`= {owner_balance} WHERE id = {owner_card_id}")
        if(type == 'Штраф'):
            base.send(f"UPDATE `cards` SET `balance`= {owner_balance} WHERE id = 0001")
        else:
            base.send(f"UPDATE `cards` SET `balance`= {owner_balance} WHERE id = 0002")
        base.send(f"UPDATE `invoices` SET `status`= 'Оплачен' WHERE id = '{invoice_id}' ")

        logchannel = self.client.get_channel(config.logschannel)
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        done_date = date.strftime("%Y-%m-%d %H:%M")

        #remove fine if type == fine
        if(type == 'Штраф'):
            fine = base.request_one(f"UPDATE fines SET status = 'Оплачен' WHERE invoice_id = '{invoice_id}'")
            fine_id = fine['id']
            notifychnl = self.client.get_channel(config.notifychnl)

            responce_chnl = discord.Embed(description=f"### 💵 Пользователь {owner.mention} оплатил штраф `{fine_id}`",color=0xD0EF6F)
            responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await notifychnl.send(embed=responce_chnl)
        
            responce_pm = discord.Embed(description=f"### 💵 Ваш штраф `{fine_id}` успешно оплачен \nПриятной игры!",color=0xD0EF6F)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await owner.send(embed=responce_pm)
            return

        #gen and send responce
        await inter.send(f"{config.accept} Счёт `{invoice_id}` успешно оплачен",ephemeral=True)

        responce_chnl_system = discord.Embed(description=f"### 💵 Пользователь {owner.mention} оплатил счёт `{invoice_id}` \nТип счёта: `{type}`\nСумма счёта: `{amount}` алмазов \n\nСчёт оформлен банкиром {invoice_author.mention} \nДата выполнения операции: `{done_date}`.",color=0xD0EF6F)
        responce_chnl_system.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl_system)

        responce_pm = discord.Embed(description=f"### 💵 Вас счёт `{invoice_id}` успешно оплачен \nТип счёта: `{type}`\nСумма счёта: `{amount}` алмазов \n\nСчёт оформлен банкиром {invoice_author.mention} \nДата выполнения операции: `{done_date}`.",color=0xD0EF6F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)

    @commands.slash_command(name="баланс", description="Показывает баланс вашей карты или указанного Пользовательа", test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, inter, member: discord.Member = None):
        guild = self.client.get_guild(inter.guild.id) 
        banker_role = discord.utils.get(guild.roles,id=1197579125037207572)

        if member != None:
            if banker_role not in inter.author.roles:
                member = inter.author
                responce = discord.Embed(description=f"### Информация по вашим картам:",color=0xEFC06F)
                responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            else:
                responce = discord.Embed(description=f"### Информация по картам {member.mention}:",color=0xEFC06F)
                responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        if member == None:
            member = inter.author
            responce = discord.Embed(description=f"### Информация по вашим картам:",color=0xEFC06F)
            responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')

        #get card info by member id
        card_info = base.request_all(f"SELECT * FROM `cards` WHERE owner_id = {member.id}")
        if card_info == ():
            await inter.send(f'{config.deny} Не нашёл зарегистрированных карт на имя {member.mention}',ephemeral=True)
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