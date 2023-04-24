import json
import discord
from discord.ext import commands
import requests
import asyncio

cooldown = set()
ignore = [909197654066593812]  # coloque ID's que o bot vai ignorar
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print(f"Conectado como {client.user}!")


@client.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(client.latency * 1000)}ms")


@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author.bot or len(message.content) <= 4 or message.author.id in ignore or message.author.id in cooldown:
        return
    await message.channel.typing()
    view = Button(message)
    cooldown.add(message.author.id)
    await message.reply("😊 **|** Opa amigo, precisa que eu te ajude com isso? Se precisar, é só pedir!", view=view)


class Button(discord.ui.View):
    def __init__(self, message):
        super().__init__(timeout=5*60)  # 5 minutos
        self.message = message

    @discord.ui.button(label='Sim', custom_id='sim', style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(content="🙂 **|** Pensando em uma resposta...", view=None)
        cooldown.add(interaction.user.id)
        try:
            headers = {
                'Authorization': 'SQUARECLOUD_API_KEY',
                'Content-Type': 'application/json'
            }
            data = {
                'question': self.message.content,
                'prompt': 'prompt'
            }
            response = requests.post(
                'https://api.squarecloud.app/v1/experimental/ai/id/create', headers=headers, data=json.dumps(data))
            if response.ok:
                id = response.json()['response']['id']
                response = requests.get(
                    f'https://api.squarecloud.app/v1/experimental/ai/{id}', headers=headers)
                if response.ok:
                    m = response.json()
                    await interaction.message.edit(content=f"{interaction.user.mention} {m.get('response') or m.get('code')}", view=None)
        except Exception as e:
            print(e)
        await asyncio.sleep(30*60)  # 30 minutos
        cooldown.remove(interaction.user.id)

    @discord.ui.button(label='Não', custom_id='nao', style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, _):
        await interaction.message.delete()
        await asyncio.sleep(30*60)  # 30 minutos
        cooldown.remove(interaction.user.id)


client.run('TOKEN')
