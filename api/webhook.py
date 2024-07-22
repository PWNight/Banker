import aiohttp
from disnake import Webhook
async def logsSend(message):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('https://discord.com/api/webhooks/1264641103542616064/Uk6LTvBRbO5NZ-hApyrDTjcy2ShTn9pjfb_a7-sPrTyyCDrjHFXLpkWo_ekMePJrZGSX',session=session)
        await webhook.send(embed=message)
async def notifySend(user_ping,message):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('https://discord.com/api/webhooks/1264636514378190868/CHbJbLvBg_vdHEHb5R2hoRE-92Sf3Hng1AjhK5FJnlt9xyn9RvlwGNnldiqztUMlTWrQ',session=session)
        return await webhook.send(content=user_ping,embed=message,wait=True)
async def notifyGet(id):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('https://discord.com/api/webhooks/1264636514378190868/CHbJbLvBg_vdHEHb5R2hoRE-92Sf3Hng1AjhK5FJnlt9xyn9RvlwGNnldiqztUMlTWrQ',session=session)
        return await webhook.fetch_message(id=id)
async def notifyEdit(id,message):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url('https://discord.com/api/webhooks/1264636514378190868/CHbJbLvBg_vdHEHb5R2hoRE-92Sf3Hng1AjhK5FJnlt9xyn9RvlwGNnldiqztUMlTWrQ',session=session)
        await webhook.edit_message(message_id=id,embed=message)