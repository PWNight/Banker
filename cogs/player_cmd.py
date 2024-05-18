import disnake as discord
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
from api.server import base, main

class PlayerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="перевести", description="💵 Переводит алмазы на указанную карту", test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give_money(self, inter, card_id: str, sum: int):
        #sum validation
        if(sum < 0 or sum == 0):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Введена некорректная сумма. Принимаются только положительные числа.',ephemeral=True)
            return
        if(sum > 1000):
            await inter.send(f'<:minecraft_deny:1080779495386140684> За раз можно перевести не более 1000 алмазов.',ephemeral=True)
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
        
        #get cards info by inter id and card id
        owner_card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {inter.author.id}")
        reciever_card_info = base.request_one(f"SELECT * FROM `cards` WHERE id = {card_id}")
        if owner_card_info == None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> На ваше имя нету зарегистрированных карт, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        if reciever_card_info == None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        
        logchannel = self.client.get_channel(1195653007703023727)
        owner_id = owner_card_info['owner_id']
        owner = await self.client.fetch_user(int(owner_id))
        owner_card_id = owner_card_info['id']
        reciever_id = reciever_card_info['owner_id']

        #check users id
        if(owner_id == reciever_id):
            await inter.send(f'<:minecraft_deny:1080779495386140684> Вы не можете перевести алмазы самому себе.',ephemeral=True)
            return
        
        reciever = await self.client.fetch_user(int(reciever_id))
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        done_date = date.strftime("%Y-%m-%d %H:%M")

        #get and calc new balance
        owner_balance = owner_card_info['balance']
        reciever_balance = reciever_card_info['balance']
        if owner_balance < sum:
            await inter.send(f'<:minecraft_deny:1080779495386140684> На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а снимается `{sum}` алмазов).',ephemeral=True)
            return
        owner_balance -= sum
        reciever_balance += sum
        
        #gen and send responce
        await inter.send(f"<:minecraft_accept:1080779491875491882> 💸 Вы перевели {sum} алмазов на карту `FW-{card_id}`.",ephemeral=True)

        responce_chnl = discord.Embed(description=f"### 💸 Пользователь {owner.mention} перевёл пользователю {reciever.mention} {sum} алмазов \nКарта владельца: `FW-{owner_card_id}`. \nКарта получателя: `FW-{card_id}`. \n\nДата оформления транзакции: `{done_date}`.",color=0xEFAF6F)
        responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await logchannel.send(embed=responce_chnl)

        responce_pm = discord.Embed(description=f"### Вы перевели пользователю {reciever.mention} {sum} алмазов \nКарта владельца: `FW-{owner_card_id}`. \nКарта получателя: `FW-{card_id}`. \nДата оформления транзакции: `{done_date}`. \n\nЕсли алмазы были переведены не вами, немедленно сообщите об этом команде проекта.",color=0xEFAF6F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        await owner.send(embed=responce_pm)

        #update balance in DB
        base.send(f'''UPDATE `cards` SET `balance` = {owner_balance} WHERE id = {owner_card_id}''')
        base.send(f'''UPDATE `cards` SET `balance` = {reciever_balance} WHERE id = {card_id}''')
        return
        
    @commands.slash_command(name="оплатить-штрафы", description="💵 Оплачивает ваши штрафы", test_guilds=[921483461016031263])
    @commands.cooldown(1,10, commands.BucketType.user)
    async def pay_fine(self, inter):
        #get owner and this card info
        owner = inter.author
        owner_card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {owner.id}")
        if owner_card_info == None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> Вы не обладаете никакими картами, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        else:
            pass
        fines_info = base.request_all(f"SELECT * FROM `fines` WHERE fined_id = {inter.author.id} AND status != 'Оплачен'")
        if fines_info == None:
            await inter.send(f'<:minecraft_deny:1080779495386140684> У вас нету штрафов.',ephemeral=True)
            return
        else:
            for x in fines_info:
                await pay(x)
        async def pay(fine_info):
            owner_card_info = base.request_one(f"SELECT * FROM `cards` WHERE owner_id = {owner.id}")
            notifychannel = self.client.get_channel(1111753012441006201)
            logchannel = self.client.get_channel(1195653007703023727)
            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            date = datetime.datetime.now(tzinfo)
            done_date = date.strftime("%Y-%m-%d %H:%M")

            #get card id, balance and calc new balance
            owner_card_id = owner_card_info['id']
            owner_balance = owner_card_info['balance']
            if owner_balance < fine_info['size']:
                await inter.send(f"<:minecraft_deny:1080779495386140684> На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` алмазов, а для оплаты нужно `{fine_info['size']}` алмазов).",ephemeral=True)
                return
            owner_balance -= fine_info['size']

            #update balance in DB
            base.send(f'''UPDATE `cards` SET `balance`= {owner_balance} WHERE id = {owner_card_id}''')
            base.send(f'''UPDATE `cards` SET `balance`= {fine_info['size']} WHERE id = 1''')
            base.send(f'''UPDATE `fines` SET `status`= 'Оплачен' WHERE id = '{fine_info['id']}' ''')

            #gen and send responce
            responce_inter = f"<:minecraft_accept:1080779491875491882> Штраф `{fine_info['id']}` успешно оплачен"
            await inter.send(responce_inter,ephemeral=True)

            responce_chnl_system = discord.Embed(description=f"### 💵 Пользователь {owner.mention} оплатил штраф `{fine_info['id']}` \nДата оформления транзакции: `{done_date}`.",color=0xD0EF6F)
            responce_chnl_system.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await logchannel.send(embed=responce_chnl_system)

            responce_chnl = discord.Embed(description=f'''### 💵 Пользователь {owner.mention} оплатил штраф `{fine_info['id']}`''',color=0xD0EF6F)
            await notifychannel.send(embed=responce_chnl)

            responce_pm = discord.Embed(description=f"### 💵 Ваш штраф `{fine_info['id']}` успешно оплачен \nДата оформления транзакции: `{done_date}`. \n\nЕсли это был не ваш штраф, немедленно обратитесь в команду проекта.",color=0xD0EF6F)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            await owner.send(embed=responce_pm)
            return

    @commands.slash_command(name="баланс", description="Показывает баланс вашей карты или указанного Пользовательа", test_guilds=[921483461016031263])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, inter, member: discord.Member = None):
        guild = self.client.get_guild(inter.guild.id) 
        banker_role = discord.utils.get(guild.roles,id=1197579125037207572)

        if member != None:
            if banker_role not in inter.author.roles:
                member = inter.author
                responce = discord.Embed(description=f'''### Информация по вашим картам:''',color=0xEFC06F)
                responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
            else:
                responce = discord.Embed(description=f'''### Информация по картам {member.mention}:''',color=0xEFC06F)
                responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')
        if member == None:
            member = inter.author
            responce = discord.Embed(description=f'''### Информация по вашим картам:''',color=0xEFC06F)
            responce.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/1053188377651970098/1238899111948976189/9.png?ex=6640f635&is=663fa4b5&hm=541eea40573fd92a3861ed259706dff887d9934650b5aab7f698c0e9842cf9bd&')

        #get card info by member id
        card_info = base.request_all(f"SELECT * FROM `cards` WHERE owner_id = {member.id}")
        if card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Не нашёл зарегистрированных карт на имя {member.mention}',ephemeral=True)
            return
        else:
            for x in card_info:
                card_id = x['id']
                card_balance = x['balance']
                card_opendate = x['date_open']
                banker = await self.client.fetch_user(int(x['banker_id']))
                responce.add_field(inline=False, name=f'Карта `FW-{card_id}`', value=f'''
                    Баланс: `{card_balance}`.
                    Оформлена банкиром {banker.mention}.
                    Дата оформления: `{card_opendate}`''')
        await inter.send(embed=responce, ephemeral=True)
        return
                
def setup(client):
    client.add_cog(PlayerCMD(client))