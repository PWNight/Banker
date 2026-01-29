import disnake as discord
from disnake.ext import commands

class Embed(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, msg: str = None):
        roleowner = discord.utils.get(ctx.guild.roles, id=922561682780332102)  # Руководитель

        if msg:
            ptext = title = description = image = thumbnail = url = footer = author = color = simple = channel = foothericon = None
            embed_values = msg.split('$')
            for i in embed_values:
                if i.strip().lower().startswith('msg'):
                    ptext = i.strip()[3:].strip()
                elif i.strip().lower().startswith('t '):
                    title = i.strip()[2:].strip()
                elif i.strip().lower().startswith('d '):
                    description = i.strip()[2:].strip()
                elif i.strip().lower().startswith('image '):
                    image = i.strip()[6:].strip()
                elif i.strip().lower().startswith('thumb '):
                    thumbnail = i.strip()[6:].strip()
                elif i.strip().lower().startswith('url '):
                    url = i.strip()[4:].strip()
                elif i.strip().lower().startswith('f '):
                    footer = i.strip()[2:].strip()
                elif i.strip().lower().startswith('a '):
                    author = i.strip()[2:].strip()
                elif i.strip().lower().startswith('c '):
                    color = i.strip()[2:].strip()
                elif i.strip().lower().startswith('m '):
                    simple = i.strip()[3:].strip()
                elif i.strip().lower().startswith('ch '):
                    channel = i.strip()[3:].strip()
                elif i.strip().lower().startswith('fu '):
                    foothericon = i.strip()[3:].strip()

            if ptext is title is description is image is thumbnail is url is footer is author is color is foothericon is None and 'field=' not in msg:
                if roleowner in ctx.author.roles:
                    return await ctx.send(content=msg)

                else:
                    return await ctx.send(content='Отсутствуют аргументы :/')
            if color:
                if "#" in color:
                    afa = color[+1]
                    bfa = color[+2]
                    cfa = color[+3]
                    dfa = color[+4]
                    efa = color[+5]
                    ffa = color[+6]
                    colo = afa + bfa + cfa + dfa + efa + ffa
                    color = discord.Color(value=int(colo, 16))
                else:
                    color = discord.Color(value=int(color, 16))
            if not color:
                color = 0x2f3136
            if ptext:
                if roleowner in ctx.author.roles:
                    if ptext == 'here' or ptext == 'everyone' or ptext.startswith('<@'):
                        if ptext == 'here':
                            ptext = '@here'
                        elif ptext == 'everyone':
                            ptext = '@everyone'
                        elif ptext.startswith('<@&'):
                            role = ptext.split()
                            role = role[0]
                            role = role[3:]
                            role = role[:-1]
                            roled = discord.utils.get(ctx.guild.roles, id=int(role))

                            if str(roled.color) != '#000000':
                                color = roled.color
                            if 'color' not in locals():
                                color = 0

                            ptext = f'{ptext}'
                else:
                    ptext = None
            if not title:
                title = " "
            if not description:
                description = " "
            if not simple:
                em = discord.Embed(title=title, description=description, color=color)
            # if not title:
            #    em = discord.Embed(description=description, color=color)
            # if not description:
            #    em = discord.Embed(title=title, color=color)
            else:
                await ctx.message.delete()
                if not channel:
                    await ctx.send(simple)
                else:
                    if roleowner in ctx.author.roles:
                        channel = channel[2:]
                        channel = channel[:-1]
                        channel = self.client.get_channel(int(channel))
                        await channel.send(simple)
                        return
                    else:
                        await ctx.send(content=ptext, embed=em)
            if url:
                em = discord.Embed(title=title, description=description, url=url, color=color)
            if author:
                if roleowner in ctx.author.roles:
                    if author == '-':
                        pass
                    else:
                        if author.startswith('<@!'):
                            author = author[3:]
                            author = author[:-1]
                        else:
                            author = author[2:]
                            author = author[:-1]
                        fm2 = await self.client.fetch_user(int(author))
                        em.set_author(name=f"{fm2.display_name}", icon_url=f"{fm2.avatar}")
            else:
                em.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.avatar}")
            # if not author:
            #    pass
            if image:
                em.set_image(url=image)
            if thumbnail:
                em.set_thumbnail(url=thumbnail)
            if footer:
                if roleowner in ctx.author.roles:
                    if footer == '-':
                        pass
                    else:
                        if foothericon:
                            if 'icon=' in footer:
                                text, icon = footer.split('icon=')
                                em.set_footer(text=text.strip()[5:], icon_url=foothericon)
                            else:
                                em.set_footer(text=f"{footer}", icon_url=foothericon)
                        else:
                            if 'icon=' in footer:
                                ext, icon = footer.split('icon=')
                                em.set_footer(text=text.strip()[5:])
                            else:
                                em.set_footer(text=f"{footer}")
                else:
                    em.set_footer(text=f"FoxWorld ©️ 2021 - 2023",
                                  icon_url="https://cdn.discordapp.com/attachments/939510519629479946/1019317064479035443/Fox5.png")
            if not footer:
                if foothericon:
                    em.set_footer(text=f"FoxWorld ©️ 2021 - 2023", icon_url=foothericon)
                else:
                    em.set_footer(text=f"FoxWorld ©️ 2021 - 2023",
                                  icon_url="https://cdn.discordapp.com/attachments/939510519629479946/1019317064479035443/Fox5.png")
            if not channel:
                await ctx.message.delete()
                await ctx.send(content=ptext, embed=em)
            else:
                if roleowner in ctx.author.roles:
                    channel = channel[2:]
                    channel = channel[:-1]
                    channel = self.client.get_channel(int(channel))
                    await ctx.message.delete()
                    await channel.send(content=ptext, embed=em)
                else:
                    await ctx.message.delete()
                    await ctx.send(content=ptext, embed=em)

        else:
            await ctx.send(
                f"Вы не указали аргументы, {ctx.author.mention}!\nВозможный способ использование:\n```\\\say $a MENTION $c HEX $t TITLE TEXT $d DESC TEXT $f FOOTER TEXT $fu URL $image URL $thumb URL```")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def edit(self, ctx, msg1, *, msg: str = None):
        msg12 = await ctx.channel.fetch_message(msg1)
        roleowner = discord.utils.get(ctx.guild.roles, id=922561682780332102)  # Руководитель

        if msg:
            ptext = title = description = image = thumbnail = url = footer = author = color = simple = channel = foothericon = None
            img = thm = ds = t = u = fo = au = colo = smpl = None
            if len(msg12.embeds) > 0:
                old_em = msg12.embeds[0]
            if old_em.description != None:
                ds = old_em.description
            if old_em.title != None:
                t = old_em.title
            if old_em.thumbnail.url != None:
                thm = old_em.thumbnail.url
            if old_em.image.url != None:
                img = old_em.image.url
            if old_em.url != None:
                u = old_em.url
            if old_em.author.name != None:
                global a
                a = old_em.author.name
            if old_em.author.icon_url != None:
                global ai
                ai = old_em.author.icon_url
            if old_em.footer.text != None:
                fo = old_em.footer.text
            if msg12.content is not None:
                smpl = msg12.content
            embed_values = msg.split('$')
            for i in embed_values:
                if i.strip().lower().startswith('msg '):
                    ptext = i.strip()[3:].strip()
                elif i.strip().lower().startswith('t '):
                    title = i.strip()[2:].strip()
                elif i.strip().lower().startswith('d '):
                    description = i.strip()[2:].strip()
                elif i.strip().lower().startswith('image '):
                    image = i.strip()[6:].strip()
                elif i.strip().lower().startswith('thumb '):
                    thumbnail = i.strip()[6:].strip()
                elif i.strip().lower().startswith('url '):
                    url = i.strip()[2:].strip()
                elif i.strip().lower().startswith('f '):
                    footer = i.strip()[2:].strip()
                elif i.strip().lower().startswith('a '):
                    author = i.strip()[2:].strip()
                elif i.strip().lower().startswith('c '):
                    color = i.strip()[2:].strip()
                elif i.strip().lower().startswith('m '):
                    simple = i.strip()[3:].strip()
                elif i.strip().lower().startswith('ch '):
                    channel = i.strip()[3:].strip()
                elif i.strip().lower().startswith('fu '):
                    foothericon = i.strip()[3:].strip()

            if ptext is title is description is image is thumbnail is url is footer is author is color is foothericon is None and 'field=' not in msg:
                if roleowner in ctx.author.roles:
                    return await ctx.send(content=msg)

                else:
                    return await ctx.send(content=f'ℹ Отсутствуют права.')
            if not ptext:
                if smpl:
                    ptext = smpl
            if not title:
                title = t
            if not description:
                description = ds
            if color:
                if "#" in color:
                    afa = color[+1]
                    bfa = color[+2]
                    cfa = color[+3]
                    dfa = color[+4]
                    efa = color[+5]
                    ffa = color[+6]
                    colo = afa + bfa + cfa + dfa + efa + ffa
                    color = discord.Color(value=int(colo, 16))
                else:
                    color = discord.Color(value=int(color, 16))
            if not color:
                color = old_em.color
            if ptext:
                if roleowner in ctx.author.roles:
                    if ptext == 'here' or ptext == 'everyone' or ptext.startswith('<@'):
                        if ptext == 'here':
                            ptext = '@here'
                        elif ptext == 'everyone':
                            ptext = '@everyone'
                        elif ptext.startswith('<@&'):
                            role = ptext.split()
                            role = role[0]
                            role = role[3:]
                            role = role[:-1]
                            roled = discord.utils.get(ctx.guild.roles, id=int(role))

                            if str(roled.color) != '#000000':
                                color = roled.color
                            if 'color' not in locals():
                                color = 0

                            ptext = f'{ptext}'
                else:
                    ptext = None
            if not simple:
                em = discord.Embed(title=title, description=description, color=color)
            if not url:
                if u:
                    em = discord.Embed(title=title, description=description, url=u, color=color)
            if url:
                em = discord.Embed(title=title, description=description, url=url, color=color)
            if author:
                if roleowner in ctx.author.roles:
                    if author == '-':
                        pass
                    else:
                        if author.startswith('<@!'):
                            author = author[3:]
                            author = author[:-1]
                        else:
                            author = author[2:]
                            author = author[:-1]
                        fm2 = await self.client.fetch_user(int(author))
                        em.set_author(name=f"{fm2.display_name}", icon_url=f"{fm2.avatar}")
                else:
                    em.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.avatar}")
            if not author:
                em.set_author(name=a, icon_url=ai)
            if not image:
                if img:
                    em.set_image(url=img)
            if image:
                em.set_image(url=image)
            if not thumbnail:
                if thm:
                    em.set_thumbnail(url=thm)
            if thumbnail:
                em.set_thumbnail(url=thumbnail)
            if footer:
                if roleowner in ctx.author.roles:
                    if footer == '-':
                        pass
                    else:
                        if foothericon:
                            if 'icon=' in footer:
                                text, icon = footer.split('icon=')
                                em.set_footer(text=text.strip()[5:], icon_url=foothericon)
                            else:
                                em.set_footer(text=f"{footer}", icon_url=foothericon)
                        else:
                            if 'icon=' in footer:
                                ext, icon = footer.split('icon=')
                                em.set_footer(text=text.strip()[5:])
                            else:
                                em.set_footer(text=f"{footer}")
                else:
                    em.set_footer(text=f"FoxWorld ©️ 2021 - 2023",
                                  icon_url="https://cdn.discordapp.com/attachments/939510519629479946/1019317064479035443/Fox5.png")
            if not footer:
                if foothericon:
                    em.set_footer(text=fo, icon_url=foothericon)
                else:
                    em.set_footer(text=f"FoxWorld ©️ 2021 - 2023",
                                  icon_url="https://cdn.discordapp.com/attachments/939510519629479946/1019317064479035443/Fox5.png")
            await ctx.message.delete()
            await msg12.edit(content=ptext, embed=em)

        else:
            if len(msg12.embeds) > 0:
                if msg12.content is not None:
                    await msg12.edit(content=msg12.content, embed=msg12.embeds[0])
                    await ctx.message.delete()
                else:
                    await msg12.edit(embed=msg12.embeds[0])
                    await ctx.message.delete()
            if len(msg12.embeds) == 0:
                await ctx.message.delete()
                await msg12.edit(content=msg12.content)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def content(self, ctx, msg):
        msg = await ctx.channel.fetch_message(msg)
        if len(msg.embeds) > 0:
            ds = t = f = c = a = img = thm = None
            embed = msg.embeds[0]
            if embed.description != None:
                ds = f'$d {embed.description}'
            else:
                ds = ''
            if embed.title != None:
                t = f'$t {embed.title}'
            else:
                t = ''
            if embed.thumbnail.url != None:
                thm = f'$thumb {embed.thumbnail.url}'
            else:
                thm = ''
            if embed.image.url != None:
                img = f'$image {embed.image.url}'
            else:
                img = ''
            if embed.footer.text != None:
                f = f'$f {embed.footer.text}'
            else:
                f = '$f -'
            if embed.author.name != None:
                a = f'$a @{embed.author.name}'
            else:
                a = f'$a -'
            if embed.colour != None:
                c = f'$c {embed.colour}'
            else:
                c = f''
            if embed.footer.icon_url != None:
                fu = f'$fu {embed.footer.icon_url}'
            else:
                fu = ''

            await ctx.message.delete()
            await ctx.send(f'```say {c} {a} {t} {ds} {f} {img} {thm} {fu}```')


def setup(client):
    client.add_cog(Embed(client))