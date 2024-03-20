import disnake as discord
import shortuuid
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
import random
from api.server import base, main

class PlayerCMD(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="перевести-ары", description="💵 Переводит АРы на указанную карту", test_guilds=[921483461016031263])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give_money(self, inter, card_id: int, sum: int):
        owner_card_info = base.request_one(f"SELECT * FROM `bank_cards` WHERE owner_id = {inter.author.id}")
        reciever_card_info = base.get_info_by_id(card_id)
        if owner_card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Вы не обладаете никакими картами, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        if reciever_card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        else:
            logchannel = self.client.get_channel(1195653007703023727)
            owner_id = owner_card_info[0]['owner_id']
            owner = await self.client.fetch_user(owner_id)
            owner_card_id = owner_card_info[0]['id']
            reciever_id = reciever_card_info[0]['owner_id']
            reciever = await self.client.fetch_user(reciever_id)

            owner_balance = owner_card_info[0]['balance']
            reciever_balance = reciever_card_info[0]['balance']
            if owner_balance < sum:
                await inter.send(f'<:minecraft_deny:1080779495386140684> На карте `FW-{card_id}` недостаточно средств (Баланс: `{owner_balance}` АРов, а снимается `{sum}` АРов).',ephemeral=True)
                return
            else:
                owner_balance -= sum
                reciever_balance += sum

            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            date = datetime.datetime.now(tzinfo)
            done_date = date.strftime("%Y-%m-%d %H:%M")
            base.send(f'''UPDATE `bank_cards` SET `balance`= {owner_balance} WHERE id = {owner_card_id}''')
            base.send(f'''UPDATE `bank_cards` SET `balance`= {reciever_balance} WHERE id = {card_id}''')

            responce_chnl = discord.Embed(description=f'''### 💸 Игрок {owner.mention} перевёл игроку {reciever.mention} {sum} АРов
                                           Карта владельца: `FW-{owner_card_id}`.
                                           Карта получателя: `FW-{card_id}`.

                                           Дата оформления транзакции: `{done_date}`.''',color=0xEFAF6F)
            responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            responce_inter = f'<:minecraft_accept:1080779491875491882> 💸 Вы перевели игроку {reciever.mention} (`FW-{card_id}`) {sum} АРов.'
            responce_pm = discord.Embed(description=f'''### Вы перевели игроку {reciever.mention} {sum} АРов
                                           Карта владельца: `FW-{owner_card_id}`.
                                           Карта получателя: `FW-{card_id}`.

                                           Дата оформления транзакции: `{done_date}`.
                                           \nЕсли АРы были переведены не вами, немедленно сообщите об этом команде проекта.''',color=0xEFAF6F)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            await logchannel.send(embed=responce_chnl)
            await owner.send(embed=responce_pm)
            await inter.send(responce_inter,ephemeral=True)
            return
        
    @commands.slash_command(name="оплатить-штрафы", description="💵 Оплачивает ваши штрафы", test_guilds=[921483461016031263])
    @commands.cooldown(1,10, commands.BucketType.user)
    async def pay_fine(self, inter):
        async def pay(fine_info):
            notifychannel = self.client.get_channel(1111753012441006201)
            logchannel = self.client.get_channel(1195653007703023727)
            owner = await self.client.fetch_user(inter.author.id)
            owner_card_id = owner_card_info[0]['id']
            owner_balance = owner_card_info[0]['balance']

            if owner_balance < fine_info['size']:
                await inter.send(f"<:minecraft_deny:1080779495386140684> На карте `FW-{owner_card_id}` недостаточно средств (Баланс: `{owner_balance}` АРов, а для оплаты нужно `{fine_info['size']}` АРов).",ephemeral=True)
                return
            else:
                owner_balance -= fine_info['size']
                pass
            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            date = datetime.datetime.now(tzinfo)
            done_date = date.strftime("%Y-%m-%d %H:%M")
            base.send(f'''UPDATE `bank_cards` SET `balance`= {owner_balance} WHERE id = {owner_card_id}''')
            base.send(f'''UPDATE `bank_cards` SET `balance`= {fine_info['size']} WHERE id = 1''')
            base.send(f'''UPDATE `fines` SET `status`= 'Оплачен' WHERE id = '{fine_info['id']}' ''')
            responce_chnl_system = discord.Embed(description=f'''### 💵 Игрок {owner.mention} оплатил штраф `{fine_info['id']}`
                                           Дата оформления транзакции: `{done_date}`.''',color=0xD0EF6F)
            responce_chnl = discord.Embed(description=f'''### 💵 Игрок {owner.mention} оплатил штраф `{fine_info['id']}`''',color=0xD0EF6F)
            responce_chnl_system.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            responce_inter = f"<:minecraft_accept:1080779491875491882> Штраф `{fine_info['id']}` успешно оплачен"
            responce_pm = discord.Embed(description=f'''### 💵 Ваш штраф `{fine_info['id']}` успешно оплачен
                                           Дата оформления транзакции: `{done_date}`.
                                           \nЕсли это был не ваш штраф, немедленно обратитесь в команду проекта.''',color=0xD0EF6F)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            await logchannel.send(embed=responce_chnl_system)
            await notifychannel.send(embed=responce_chnl)
            await owner.send(embed=responce_pm)
            await inter.send(responce_inter,ephemeral=True)
        
        owner_card_info = base.request_one(f"SELECT * FROM `bank_cards` WHERE owner_id = {inter.author.id}")
        if owner_card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Вы не обладаете никакими картами, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        else:
            pass
        fines_info = base.request_all(f"SELECT * FROM `fines` WHERE fined_id = {inter.author.id} AND status != 'Оплачен'")
        if fines_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> У вас нету штрафов.',ephemeral=True)
            return
        else:
            for x in fines_info:
                await pay(x)
    @commands.slash_command(name="баланс", description="💰 Отображает баланс вашей карты", test_guilds=[921483461016031263])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give_money(self, inter):
        owner_card_info = base.request_one(f"SELECT * FROM `bank_cards` WHERE owner_id = {inter.author.id}")
        if owner_card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Вы не обладаете никакими картами, обратитесь в отделение банка для оформления карты.',ephemeral=True)
            return
        else:
            owner_card_id = owner_card_info[0]['id']
            owner_balance = owner_card_info[0]['balance']
            responce_inter = f'<:minecraft_accept:1080779491875491882> 💰 Баланс вашей карты (`FW-{owner_card_id}`) - `{owner_balance}` АРов.'

            await inter.send(responce_inter,ephemeral=True)
            return
                
def setup(client):
    client.add_cog(PlayerCMD(client))