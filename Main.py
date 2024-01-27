import discord
from keys import *
from discord.ext import commands
from Scout import *

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

def is_me(m):
    return m.author == client.user

@client.event
async def on_ready():
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == 'scout-bot':
                await channel.purge(check=is_me)
                print([thread.member_count for thread in channel.threads])
                for thread in channel.threads:
                    if thread.member_count <= 1:
                        await thread.delete()
                await channel.send(content="Pick the event you're at", view=EventSel(), silent=True)
                print(channel.name)
        print(guild.name)
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(discordKey)