import discord
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    print(f"{message.author} wrote: {message.content}")

    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')


class Student:
    def __init__(self, message):
        self.name = message.author


client.run(":)")
