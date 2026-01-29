import disnake as discord
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
import random2
from api import main, base
from configs import config

class BankerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="создать-карту", description="💳 Создаёт банковскую карту на указанного пользователя", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def create_card(self, inter, member: discord.Member):
        await inter.response.defer(ephemeral = True)
        
        #func gen card and validate card id (example: 0011)
        def gen_id():
            random_int = random2.randint(1,9999)
            random_int = str(random_int)
            if len(random_int) == 1:
                random_int = '000' + random_int
            if len(random_int) == 2:
                random_int = '00' + random_int
            if len(random_int) == 3:
                random_int = '0' + random_int
            return random_int
        
        def validate_id():
            card_id = gen_id()
            is_card_exists = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
            if is_card_exists != None:
                validate_id()
            else:
                return card_id
        card_id = validate_id()
        
        #check if member != server player
        guild = inter.guild
        player_role = discord.utils.get(guild.roles,id=1172204202328592455)    
        if(player_role not in member.roles):
            await inter.send(f'{config.deny} Пользователь не является игроком проекта.',ephemeral=True)
            return
            
        #get member card info
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {member.id}")
        if card_info != None:
            await inter.send(f'{config.deny} У пользователя уже есть зарегистрированная карта `FW-{card_info["id"]}`.',ephemeral=True)
            return
        
        logchannel = self.client.get_channel(config.logschannel)
        owner = member
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        date = str(date).split('.')
        date = date[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = datetime.datetime.timestamp(date_format)
        timestamp = f"<t:{timestamp}:f>"

        #insert new card in DB
        base.send(f'''INSERT INTO `cards`(`id`, `owner_id`, `banker_id`) VALUES ('{card_id}','{owner.id}','{banker.id}')''')

        #gen and send responce message
        await inter.send(f'{config.accept} Карта `FW-{card_id}` для пользователя {owner.mention} успешно оформлена.',ephemeral=True)

        responce_chnl_system = discord.Embed(description=f"### 💳 Пользователь {owner.mention} оформил карту `FW-{card_id}` \nКарту оформил банкир {banker.mention}. \nДата оформления: {timestamp}.",color=0x80D8ED)
        responce_chnl_system.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl_system)

        responce_pm = discord.Embed(description=f"### Вы успешно оформили карту `FW-{card_id}` \nКарту оформил банкир {banker.mention}. \nДата оформления: {timestamp}. \n\nЕсли вы не оформляли карту, немедленно сообщите об этом в <#1187849294942842900>.",color=0x80D8ED)
        responce_pm.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)

    @commands.slash_command(name="удалить-карту", description="💳 Удаляет указанную банковскую карту", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def delete_card(self, inter, card_id: str):
        await inter.response.defer(ephemeral = True)
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
            
        #get member card info
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if card_info == None:
            await inter.send(f'{config.deny} Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
                
        logchannel = self.client.get_channel(config.logschannel)
        owner = await self.client.fetch_user(card_info['owner_id'])
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = str(datetime.datetime.now(tzinfo)).split('.')[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
        timestamp = f"<t:{timestamp}:f>"

        #insert new card in DB
        base.send(f"DELETE FROM `cards` WHERE id = {card_id}")

        #gen and send responce message
        await inter.send(f'{config.accept} Карта `FW-{card_id}` пользователя {owner.mention} успешно удалена.',ephemeral=True)

        responce_chnl_system = discord.Embed(description=f"### 💳 Карта `FW-{card_id}` пользователя {owner.mention} удалена \nКарта удалена банкиром {banker.mention}. \n\nДата удаления: {timestamp}.",color=0x80D8ED)
        responce_chnl_system.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl_system)

        responce_pm = discord.Embed(description=f"### Ваша карта `FW-{card_id}` была удалена \nКарта удалена банкиром {banker.mention}. \nДата удаления: {timestamp}. \n\nЕсли карта была удалена не по вашему заявлению - обратитесь в <#1187849294942842900>.",color=0x80D8ED)
        responce_pm.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)
    
    @commands.slash_command(name="снять-алмазы", description="💸 Снимает алмазы с указанной карты", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def take_money(self, inter, card_id: str, sum: int):
        await inter.response.defer(ephemeral = True)
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'{config.deny} Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 5000):
            await inter.send(f'{config.deny} За раз можно снять не более 5000 алмазов.',ephemeral=True)
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

        #get card info by card id
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if card_info == None:
            await inter.send(f'{config.deny} Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        
        logchannel = self.client.get_channel(config.logschannel)
        owner = await self.client.fetch_user(card_info['owner_id'])
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = str(datetime.datetime.now(tzinfo)).split('.')[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
        timestamp = f"<t:{timestamp}:f>"

        #get balance and calc new
        balance = int(card_info['balance'])
        if balance < sum:
            await inter.send(f'{config.deny} На карте `FW-{card_id}` недостаточно средств. Баланс: `{balance}` алмазов, а снимается `{sum}` алмазов.',ephemeral=True)
            return
        new_balance = balance - sum

        #update card balance in DB
        base.send(f"UPDATE `cards` SET `balance`= {new_balance} WHERE id = {card_id}")

        #gen and send responce
        await inter.send(f'{config.accept} Вы сняли с карты пользователя {owner.mention} (`FW-{card_id}`) {sum} алмазов.',ephemeral=True)

        responce_chnl_system = discord.Embed(description=f"### 💸 Пользователь {owner.mention} снял {sum} алмазов с карты `FW-{card_id}` \nБаланс: ~~{balance}~~ -> {new_balance} алмазов. \nТранзакция оформлена банкиром {banker.mention}. \nДата оформления транзакции: {timestamp}.",color=0x80d8ed)
        responce_chnl_system.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl_system)

        responce_pm = discord.Embed(description=f"### Вы сняли {sum} алмазов с карты `FW-{card_id}` \nБаланс: ~~{balance}~~ -> {new_balance} алмазов. \nТранзакция оформлена банкиром {banker.mention}. \nДата оформления транзакции: {timestamp}.",color=0x80d8ed)
        responce_pm.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)
        
    @commands.slash_command(name="пополнить-карту", description="💸 Пополняет карту пользователя", guild_ids=[921483461016031263], test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def grant_money(self, inter, card_id: str, sum: int):
        await inter.response.defer(ephemeral = True)
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'{config.deny} Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 5000):
            await inter.send(f'{config.deny} За раз можно пополнить не более 5000 алмазов.',ephemeral=True)
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

        #gen card info by card id
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if card_info == None:
            await inter.send(f'{config.deny} Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        
        logchannel = self.client.get_channel(config.logschannel)
        owner_id = card_info['owner_id']
        owner = await self.client.fetch_user(owner_id)
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = str(datetime.datetime.now(tzinfo)).split('.')[0]
        date_format = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        timestamp = int(str(datetime.datetime.timestamp(date_format)).split('.')[0])
        timestamp = f"<t:{timestamp}:f>"

        #get balance and calc new
        balance = int(card_info['balance'])
        new_balance = balance + sum

        #update card balance in DB
        base.send(f"UPDATE `cards` SET `balance` = {new_balance} WHERE id = {card_id}")

        #gen and send responce
        await inter.send(f'{config.accept} Вы пополнили карту пользователя {owner.mention} (`FW-{card_id}`) на {sum} алмазов.',ephemeral=True)

        responce_chnl_system = discord.Embed(description=f"### 💸 Пользователь {owner.mention} пополнил карту `FW-{card_id}` на {sum} алмазов \nБаланс: ~~{balance}~~ -> {new_balance} алмазов. \nТранзакция оформлена банкиром {banker.mention}. \nДата оформления транзакции: {timestamp}.",color=0x80d8ed)
        responce_chnl_system.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl_system)

        responce_pm = discord.Embed(description=f"### Вы пополнили карту `FW-{card_id}` на {sum} алмазов \nБаланс: ~~{balance}~~ -> {new_balance} алмазов. \nТранзакция оформлена банкиром {banker.mention}. \nДата оформления транзакции: {timestamp}.",color=0x80d8ed)
        responce_pm.set_footer(text=f'{main.copyright()}', icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)

def setup(client):
    client.add_cog(BankerCMD(client))