import disnake as discord
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
import random
from api.server import base, main

class BankerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="создать-карту", description="💳 Создаёт банковскую карту на указанного пользователя", test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def create_card(self, inter, member: discord.Member):
        #func gen card if (example: 0011)
        def gen_id():
            random_int = random.randint(1,9999)
            random_int = str(random_int)
            if len(random_int) == 1:
                random_int = '000' + random_int
            if len(random_int) == 2:
                random_int = '00' + random_int
            if len(random_int) == 3:
                random_int = '0' + random_int
            if len(random_int) == 4:
                pass
            return random_int
        
        #check if member != server player
        guild = inter.guild
        player_role = discord.utils.get(guild.roles,id=1197579125037207572)    
        if(player_role not in member.roles):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Пользователь не является игроком проекта.',ephemeral=True)
            return
            
        #get member card info
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {member.id}")
        if card_info != None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> У пользователя уже есть зарегистрированная карта (`FW-{card_info["id"]}`)',ephemeral=True)
            return
                
        logchannel = self.client.get_channel(1195653007703023727)
        card_id = gen_id()
        owner = member
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        open_date = date.strftime("%Y-%m-%d %H:%M")

        #insert new card in DB
        base.send(f'''INSERT INTO `cards`(`id`, `owner_id`, `banker_id`, `canbe_closed`, `balance`, `balance_limit`) VALUES ('{card_id}','{owner.id}','{banker.id}',false,0,0)''')

        #gen and send responce message
        responce_inter = f'<:minecraft_accept:1080779491875491882> Карта `FW-{card_id}` для пользователя {owner.mention} успешно оформлена.'
        await inter.send(responce_inter,ephemeral=True)

        responce_chnl = discord.Embed(description=f"### 💳 Пользователь {owner.mention} оформил карту \nНомер карты: `FW-{card_id}`. \n\nОформлена банкиром {banker.mention}. \n\nДата оформления: `{open_date}`.",color=0xEFD46F)
        responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl)

        responce_pm = discord.Embed(description=f"### На ваше имя оформлена карта \nНомер карты: `FW-{card_id}`. \n\nОформлена банкиром: {banker.mention}. \n\nДата оформления: `{open_date}`. \n\nЕсли вы не запрашивали оформление карты, немедленно сообщите об этом в службу поддержки.",color=0xEFD46F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)
        return

    @commands.slash_command(name="снять-алмазы", description="💸 Снимает алмазы с указанной карты", test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def take_money(self, inter, card_id: str, sum: int):
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 1000):
            await inter.send(f'<:minecraft_deny:1080779495386140684> За раз можно снять не более 1000 алмазов.',ephemeral=True)
            return
        
        #card id validation
        if(len(card_id) > 4):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Неправильный номер карты. Пример номера: `0001`.',ephemeral=True)
            return
        try:
            int(card_id)
        except ValueError:
            await inter.send(f'<:minecraft_deny:1080779495386140684> Неправильный номер карты. Пример номера: `0001`.',ephemeral=True)
            return
        
        #get card info by card id
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if card_info == None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        
        logchannel = self.client.get_channel(1195653007703023727)
        owner_id = card_info['owner_id']
        owner = await self.client.fetch_user(owner_id)
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        done_date = date.strftime("%Y-%m-%d %H:%M")

        #get balance and calc new
        balance = card_info['balance']
        if balance < sum:
            await inter.send(f'<:minecraft_deny:1080779495386140684> На карте `FW-{card_id}` недостаточно средств (Баланс: `{balance}` алмазов, а снимается `{sum}` алмазов).',ephemeral=True)
            return
        balance -= sum

        #update card balance in DB
        base.send(f'''UPDATE `cards` SET `balance`= {balance} WHERE id = {card_id}''')

        #gen and send responce
        responce_inter = f'<:minecraft_accept:1080779491875491882> Вы сняли с карты пользователя {owner.mention} (`FW-{card_id}`) {sum} алмазов.'
        await inter.send(responce_inter,ephemeral=True)

        responce_chnl = discord.Embed(description=f"### 💸 Пользователь {owner.mention} снял {sum} алмазов с карты \nНомер карты: `FW-{card_id}`. \nНовый баланс: `{balance}` алмазов. \n\nТранзакция оформлена банкиром: {banker.mention}. \nДата оформления транзакции: `{done_date}`.",color=0xEF946F)
        responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl)

        responce_pm = discord.Embed(description=f"### 💸 С вашей карты снято {sum} алмазов \nНомер карты: `FW-{card_id}`. \nНовый баланс: `{balance}` алмазов. \n\nТранзакция оформлена банкиром: {banker.mention}. \nДата оформления транзакции: `{done_date}`. \n\nЕсли алмазы были сняты не вами, немедленно сообщите об этом в службу поддержки.",color=0xEF946F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)
        return
        
    @commands.slash_command(name="пополнить-карту", description="💸 Пополняет карту пользователя", test_guilds=[921483461016031263])
    @commands.has_role(1197579125037207572)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def grant_money(self, inter, card_id: str, sum: int):
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 1000):
            await inter.send(f'<:minecraft_deny:1080779495386140684> За раз можно пополнить не более 1000 алмазов.',ephemeral=True)
            return
        
        #card id validation
        if(len(card_id) > 4):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Неправильный номер карты. Пример номера: `0001`.',ephemeral=True)
            return
        try:
            int(card_id)
        except ValueError:
            await inter.send(f'<:minecraft_deny:1080779495386140684> Неправильный номер карты. Пример номера: `0001`.',ephemeral=True)
            return

        #gen card info by card id
        card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if card_info == None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        logchannel = self.client.get_channel(1195653007703023727)
        owner_id = card_info['owner_id']
        owner = await self.client.fetch_user(owner_id)
        banker = inter.author
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        done_date = date.strftime("%Y-%m-%d %H:%M")

        #get balance and calc new
        balance = card_info['balance']
        balance += sum

        #update card balance in DB
        base.send(f'''UPDATE `cards` SET `balance`= {balance} WHERE id = {card_id}''')

        #gen and send responce
        responce_inter = f'<:minecraft_accept:1080779491875491882> Вы пополнили карту пользователя {owner.mention} (`FW-{card_id}`) на {sum} алмазов.'
        await inter.send(responce_inter,ephemeral=True)
        responce_chnl = discord.Embed(description=f"### 💸 Пользователь {owner.mention} пополнил карту на {sum} алмазов \nНомер карты: `FW-{card_id}`. \nНовый баланс: `{balance}` алмазов. \n\nТранзакция оформлена банкиром: {banker.mention}. \nДата оформления транзакции: `{done_date}`.",color=0xC4EF6F)
        responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl)
        responce_pm = discord.Embed(description=f"### 💸 Ваша карта пополнена на {sum} алмазов \nНомер карты: `FW-{card_id}`. \nНовый баланс: `{balance}` алмазов. \n\nТранзакция оформлена банкиром: {banker.mention}. \nДата оформления транзакции: `{done_date}`. \n\nЕсли алмазы были пополнены не вами, немедленно сообщите об этом в службу поддержки.",color=0xC4EF6F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)
        return

def setup(client):
    client.add_cog(BankerCMD(client))