import aiohttp
from disnake import Webhook
async def logsSend(message):
    async with aiohttp.ClientSession() as session:
        logsWebhook = Webhook.from_url('https://discord.com/api/webhooks/1264641103542616064/Uk6LTvBRbO5NZ-hApyrDTjcy2ShTn9pjfb_a7-sPrTyyCDrjHFXLpkWo_ekMePJrZGSX',session=session)
        await logsWebhook.send(embed=message)
async def notionSend(message):
    async with aiohttp.ClientSession() as session:
        logsWebhook = Webhook.from_url('https://discord.com/api/webhooks/1264641103542616064/Uk6LTvBRbO5NZ-hApyrDTjcy2ShTn9pjfb_a7-sPrTyyCDrjHFXLpkWo_ekMePJrZGSX',session=session)
        await logsWebhook.send(embed=message)