import disnake as discord
import shortuuid
import datetime
from datetime import timezone, timedelta
from disnake.ext import commands
import random
from api.server import base, main

class Banker(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.slash_command(name="создать-счёт", description="💳 Создаёт счёт на указанного игрока", test_guilds=[921483461016031263])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def create_card(self, inter, member: discord.Member):
        logchannel = self.client.get_channel(1195653007703023727)
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
        card_id = gen_id()
        owner = member
        banker = inter.author

        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        date = datetime.datetime.now(tzinfo)
        open_date = date.strftime("%Y-%m-%d %H:%M")
        base.send(f'''INSERT INTO `bank_cards`(`id`, `owner_id`, `banker_id`, `open_date`, `balance`, `balance_limit`) VALUES ('{card_id}','{owner.id}','{banker.id}','{open_date}',0,0)''')

        responce_chnl = discord.Embed(description=f'''### Игрок {owner.mention} оформил карту
                                       Номер карты: `FW-{card_id}`.

                                       Оформлена банкиром: {banker.mention}.

                                       Дата оформления: `{open_date}`.''',color=0xAFEF6F)
        responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
        responce_inter = f'<:minecraft_accept:1080779491875491882> Карта для игрока {owner.mention} успешно оформлена.'
        responce_pm = discord.Embed(description=f'''### На ваше имя зарегистрирована карта
                                       Номер карты: `FW-{card_id}`.

                                       Оформлена банкиром: {banker.mention}.

                                       Дата оформления: `{open_date}`.
                                       \nЕсли вы не запрашивали оформление карты, немедленно сообщите об этом команде проекта.''',color=0xAFEF6F)
        responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
        await logchannel.send(embed=responce_chnl)
        await owner.send(embed=responce_pm)
        await inter.send(responce_inter,ephemeral=True)
        return

    @commands.slash_command(name="снять-ары", description="💸 Снимает ары с указанного счёта", test_guilds=[921483461016031263])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def take_money(self, inter, card_id: int, sum: int):
        card_info = base.get_info_by_id(card_id)
        print(card_info)
        if card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        else:
            logchannel = self.client.get_channel(1195653007703023727)
            owner_id = card_info[0]['owner_id']
            owner = await self.client.fetch_user(owner_id)
            banker = inter.author
            balance = card_info[0]['balance']
            if balance < sum:
                await inter.send(f'<:minecraft_deny:1080779495386140684> На карте `FW-{card_id}` недостаточно средств (Баланс: `{balance}` АРов, а снимается `{sum}` АРов).',ephemeral=True)
                return
            else:
                newBalance = balance - sum
            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            date = datetime.datetime.now(tzinfo)
            open_date = date.strftime("%Y-%m-%d %H:%M")
            base.send(f'''UPDATE `bank_cards` SET `balance`= {newBalance} WHERE id = {card_id}''')

            responce_chnl = discord.Embed(description=f'''### Игрок {owner.mention} снял {sum} АРов с карты
                                           Номер карты: `FW-{card_id}`.

                                           Транзакция оформлена банкиром: {banker.mention}.

                                           Дата оформления транзакции: `{open_date}`.''',color=0xEFAF6F)
            responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            responce_inter = f'<:minecraft_accept:1080779491875491882> Карта для игрока {owner.mention} успешно оформлена.'
            responce_pm = discord.Embed(description=f'''### С вашей карты снято {sum} АРов
                                           Номер карты: `FW-{card_id}`.

                                           Транзакция оформлена банкиром: {banker.mention}.

                                           Дата оформления транзакции: `{open_date}`.
                                           \nЕсли АРы были сняты не вами, немедленно сообщите об этом команде проекта.''',color=0xEFAF6F)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            await logchannel.send(embed=responce_chnl)
            await owner.send(embed=responce_pm)
            await inter.send(responce_inter,ephemeral=True)
            return
        
    @commands.slash_command(name="пополнить-счёт", description="💸 Пополняет счёт игрока", test_guilds=[921483461016031263])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def give_money(self, inter, card_id: int, sum: int):
        card_info = base.get_info_by_id(card_id)
        print(card_info)
        if card_info == ():
            await inter.send(f'<:minecraft_deny:1080779495386140684> Карта `FW-{card_id}` не найдена. Убедитесь, что вы ввели правильный номер.',ephemeral=True)
            return
        else:
            logchannel = self.client.get_channel(1195653007703023727)
            owner_id = card_info[0]['owner_id']
            owner = await self.client.fetch_user(owner_id)
            banker = inter.author
            balance = card_info[0]['balance']
            newBalance = balance + sum

            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            date = datetime.datetime.now(tzinfo)
            open_date = date.strftime("%Y-%m-%d %H:%M")
            base.send(f'''UPDATE `bank_cards` SET `balance`= {newBalance} WHERE id = {card_id}''')

            responce_chnl = discord.Embed(description=f'''### Игрок {owner.mention} пополнил карту на {sum} АРов
                                           Номер карты: `FW-{card_id}`.

                                           Карта была пополнена в отделении банка.

                                           Транзакция оформлена банкиром: {banker.mention}.

                                           Дата оформления транзакции: `{open_date}`.''',color=0xEFAF6F)
            responce_chnl.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            responce_inter = f'<:minecraft_accept:1080779491875491882> Карта для игрока {owner.mention} успешно оформлена.'
            responce_pm = discord.Embed(description=f'''### Ваша карта пополнена на {sum} АРов
                                           Номер карты: `FW-{card_id}`.

                                           Карта была пополнена в отделении банка.

                                           Транзакция оформлена банкиром: {banker.mention}.

                                           Дата оформления транзакции: `{open_date}`.
                                           \nЕсли АРы были пополнены не вами, немедленно сообщите об этом команде проекта.''',color=0xEFAF6F)
            responce_pm.set_footer(text=f'{main.copyright()}',icon_url=f'https://cdn.discordapp.com/attachments/856561382484475904/1195663985832366090/5526-icon-bank.png?ex=65b4cfdc&is=65a25adc&hm=58ceeeb52340e12b7bfd360db0dbdc048b0954800528f43c9bb7c3a4ab50ba4d&')
            await logchannel.send(embed=responce_chnl)
            await owner.send(embed=responce_pm)
            await inter.send(responce_inter,ephemeral=True)
            return

def setup(client):
    client.add_cog(Banker(client))