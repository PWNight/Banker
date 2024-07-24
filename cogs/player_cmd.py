import disnake as discord
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
from api import base
from api import main
from api import webhook
from configs import config

class PlayerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="перевести", description="💵 Переводит алмазы на указанную карту", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_money(self, inter, card_id: str, sum: int, comment: str):
        #start response
        await inter.response.defer(ephemeral = True)
        embed = discord.Embed(description=f"<a:load:1256975206455447643> Обрабатываю ваш запрос, ожидайте..", color=0x2f3136)
        await inter.send(embed = embed, ephemeral = True)

        #sum validation
        if(sum < 0 or sum == 0):
            embed.description = f'{config.deny} Введена некорректная сумма. Принимаются только положительные числа.'
            await inter.edit_original_response(embed = embed)
            return
        if(sum > 5000):
            embed.description = f'{config.deny} За раз можно перевести не более 5000 алмазов.'
            await inter.edit_original_response(embed = embed)
            return
        
        #card id validation
        if(len(card_id) != 4):
            embed.description = f'{config.deny} Неправильный номер карты. Пример номера: `0001`.'
            await inter.edit_original_response(embed = embed)
            return
        try:
            int(card_id)
        except ValueError:
            embed.description = f'{config.deny} Неправильный номер карты. Пример номера: `0001`.'
            await inter.edit_original_response(embed = embed)
            return
        card_id = int(card_id)
        
        #get cards info by inter id and card id
        owner_card = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {inter.author.id}")
        reciever_card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if owner_card == None:
            embed.description = f'{config.deny} У вас нету банковской карты. Обратитесь в отделение банка для её оформления.'
            await inter.edit_original_response(embed = embed)
            return
        if reciever_card_info == None:
            embed.description = f'{config.deny} Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.'
            await inter.edit_original_response(embed = embed)
            return
        
        #check users id
        owner_id = owner_card['owner_id']
        reciever_id = reciever_card_info['owner_id']
        if(owner_id == reciever_id):
            embed.description = f'{config.deny} Вы не можете перевести алмазы самому себе.'
            await inter.edit_original_response(embed = embed)
            return
        
        owner = await self.client.fetch_user(int(owner_id))
        owner_card_id = owner_card['id']
        reciever = await self.client.fetch_user(int(reciever_id))
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = str(datetime.datetime.now(tzinfo)).split('.')[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
        timestamp = f"<t:{timestamp}:f>"

        #get and calc new balance
        owner_balance = int(owner_card['balance'])
        reciever_balance = int(reciever_card_info['balance'])
        if owner_balance < sum:
            await inter.send(f'{config.deny} На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а снимается `{sum}` алмазов).',ephemeral=True)
            return
        owner_balance -= sum
        reciever_balance += sum
        
        #update balance in DB
        base.send(f"UPDATE `cards` SET `balance` = {owner_balance} WHERE id = {owner_card_id}")
        base.send(f"UPDATE `cards` SET `balance` = {reciever_balance} WHERE id = {card_id}")

        logs_message = discord.Embed(description=f"### 💸 Пользователь {owner.mention} перевёл пользователю {reciever.mention} {sum} алмазов \nКарта владельца: `FW-{owner_card_id}`. \nКарта получателя: `FW-{card_id}`. \n\nДата оформления транзакции: {timestamp}. \nКомментарий к операции: `{comment}`.",color=0xEFAF6F)
        logs_message.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await webhook.logsSend(logs_message)

        responce_owner_pm = discord.Embed(description=f"### Вы перевели {sum} алмазов на карту `FW-{card_id}` \nДата оформления транзакции: {timestamp}. \nКомментарий к операции: `{comment}`.",color=0xEFAF6F)
        responce_owner_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_owner_pm)

        responce_reciever_pm = discord.Embed(description=f"### Вы получили {sum} алмазов на карту `FW-{card_id}` \nПеревод поступил от {owner.mention} (`FW-{owner_card_id}`) \nДата оформления транзакции: {timestamp}. \nКомментарий к операции: `{comment}`.",color=0xEFAF6F)
        responce_reciever_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await reciever.send(embed=responce_reciever_pm)

        #gen and send responce
        embed.description = f'{config.accept} 💸 Вы перевели {sum} алмазов на карту `FW-{card_id}`.'
        await inter.edit_original_response(embed = embed)
        
    @commands.slash_command(name="оплатить-счёт", description="💵 Оплачивает указанный счёт", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.cooldown(1,10, commands.BucketType.user)
    async def pay_invoice(self, inter, invoice_id = str):
        #start response
        await inter.response.defer(ephemeral = True)
        embed = discord.Embed(description=f"<a:load:1256975206455447643> Обрабатываю ваш запрос, ожидайте..", color=0x2f3136)
        await inter.send(embed = embed, ephemeral = True)

        #card id validation
        if(len(invoice_id) != 6):
            embed.description = f'{config.deny} Неправильный номер счёта. Пример номера: `000001`.'
            await inter.edit_original_response(embed = embed)
            return
        try:
            int(invoice_id)
        except ValueError:
            embed.description = f'{config.deny} Неправильный номер счёта. Пример номера: `000001`.'
            await inter.edit_original_response(embed = embed)
            return

        #get owner card info
        owner_card = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {inter.author.id}")
        if owner_card == None:
            embed.description = f'{config.deny} У вас нету банковской карты. Обратитесь в отделение банка для её оформления.'
            await inter.edit_original_response(embed = embed)
            return

        #check is invoice exists
        invoice = base.request_one(f"SELECT * FROM `invoices` WHERE id = '{invoice_id}' AND status NOT IN ('Оплачен','Отменён')")
        if invoice == None:
            invoice = base.request_one(f"SELECT * FROM `invoices` WHERE id = '{invoice_id}'")
            if invoice == None:
                embed.description = f'{config.deny} Счёт `{invoice_id}` не найден.'
                await inter.edit_original_response(embed = embed)
            else:
                if invoice['status'] == 'Оплачен':
                    embed.description = f'{config.deny} Счёт `{invoice_id}` уже оплачен.'
                    await inter.edit_original_response(embed = embed)
                else:
                    embed.description = f'{config.deny} Счёт `{invoice_id}` уже отменён.'
                    await inter.edit_original_response(embed = embed)
            return
        
        #get invoice info
        owner = await self.client.fetch_user(int(invoice['for_userid']))
        amount = int(invoice['amount'])
        type = invoice['type']

        #get card id, balance and calc new balance
        owner_card_id = int(owner_card['id'])
        owner_balance = int(owner_card['balance'])
        if owner_balance < amount:
            embed.description = f'{config.deny} На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а для оплаты нужно `{amount}` алмазов).'
            await inter.edit_original_response(embed = embed)
            return
        owner_balance -= amount

        #update reciever balance and invoice status
        base.send(f"UPDATE `cards` SET `balance` = '{owner_balance}' WHERE id = '{owner_card_id}'")
        
        #logic for fines invoices
        if type == 'Штраф':
            #get fine info
            fine = base.request_one(f"SELECT id,message_id FROM fines WHERE invoice_id = '{invoice_id}'")
            fine_id = fine['id']

            #gen timestamp
            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            date = str(datetime.datetime.now(tzinfo)).split('.')[0]
            date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
            timestamp = f"<t:{timestamp}:f>"

            #get goverment balance
            goverment_card = base.request_one("SELECT * FROM cards WHERE id = '0001'")
            gov_balance = goverment_card['balance']

            #prepare log message
            logs_message = discord.Embed(color=0x80d8ed)
            logs_message.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')

            #check if goverment == reciever
            reciever_user_id = int(invoice['to_userid'])
            if(reciever_user_id != 1195315985532604506):
                reciever_card = base.request_one(f"SELECT * FROM cards WHERE owner_id = '{reciever_user_id}'")
                reciever_card_id = reciever_card['id']

                #calc and update balances
                user_balance = int(reciever_card['balance'])
                gov_balance += amount * (1 - 90/100)
                user_balance += amount * (1 - 20/100)
                base.send(f"UPDATE `cards` SET `balance` = '{user_balance}' WHERE id = '{reciever_card_id}'")

                #send message in logs
                logs_message.description = f"### 💵 Штраф {fine_id} оплачен \n`{amount}` алмазов было распределено между получателем и правительством. \n`{amount * (1 - 10/100)}` алмазов было направлено получателю <@{reciever_user_id}> \n`{amount * (1 - 90/100)}` алмазов было направлено в казну правительства. \n\nДата выполнения операции: {timestamp}"
                await webhook.logsSend(logs_message)
            else:
                #calc goverment balance
                gov_balance += amount
                
                #send message in logs
                logs_message.description = f"### 💵 Штраф {fine_id} оплачен \n`{amount}` алмазов было направлено в казну правительства. \n\nДата выполнения операции: {timestamp}"
                await webhook.logsSend(logs_message)

            #update goverment balance
            base.send(f"UPDATE `cards` SET `balance` = '{gov_balance}' WHERE id = '0001'")
            
            #update invoice and fine status
            base.send(f"UPDATE `invoices` SET `status`= 'Оплачен' WHERE id = '{invoice_id}'")
            base.send(f"UPDATE fines SET status = 'Оплачен' WHERE invoice_id = '{invoice_id}'")

            #get fine message
            msg_id = fine['message_id']
            msg = await webhook.notifyGet(msg_id)
            msg_embed = msg.embeds[0]

            #prepare message to user
            responce_pm = discord.Embed(color=0x80d8ed)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')

            #edit fine message and send message to user
            msg_embed.description = msg_embed.description.replace("**","~~")
            if(owner != inter.author):
                msg_embed.description = f"{msg_embed.description} \n\n**Штраф оплачен игроком {inter.author.mention}.** \nДата оплаты: {timestamp}"
                responce_pm.description = f"### Ваш штраф `{fine_id}` оплачен игроком {inter.author.mention} \nПриятной игры!"
            else:
                msg_embed.description = f"{msg_embed.description} \n\n**Штраф оплачен.** \nДата оплаты: {timestamp}"
                responce_pm.description = f"### Ваш штраф `{fine_id}` успешно оплачен \nПриятной игры!"
            await webhook.notifyEdit(msg_id,msg_embed)
            await owner.send(embed=responce_pm)
        else:
            pass
            #TODO: реализовать иные виды счетов и логику под них
        embed.description = f'{config.accept} Счёт `{invoice_id}` успешно оплачен.'
        await inter.edit_original_response(embed = embed)

    @commands.slash_command(name="баланс", description="💳 Показывает баланс вашей карты или указанного пользователя", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, inter, member: discord.Member = None):
        #start response
        await inter.response.defer(ephemeral = True)
        embed = discord.Embed(description=f"<a:load:1256975206455447643> Обрабатываю ваш запрос, ожидайте..", color=0x2f3136)
        await inter.send(embed = embed, ephemeral = True)

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
            embed.description = f'{config.deny} У игрока {member.mention} нету карт.'
            await inter.edit_original_response(embed = embed)
            return
        
        #gen and send responce
        for x in card_info:
            card_id = x['id']
            card_balance = x['balance']
            card_opendate = x['date_open']
            banker = await self.client.fetch_user(int(x['banker_id']))
            responce.add_field(inline=False, name=f'Карта `FW-{card_id}`', value=f"Баланс: `{card_balance}`. \nОформлена банкиром {banker.mention}. \nДата оформления: `{card_opendate}`")
        await inter.edit_original_response(embed = responce)
                
def setup(client):
    client.add_cog(PlayerCMD(client))