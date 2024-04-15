import discord, os, youtubeDl
from discord.ext import commands
from discord import app_commands
from typing import Optional

token = open('token.txt', 'r').readline()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)

queue = []

@bot.event #gli eventi hanno questo decoratore
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("listening to youtube"))
    synced = await bot.tree.sync()
    print(f"{len(synced)} commands loaded.")
    print(f'We have logged in as {bot.user}')

@bot.tree.command(name='ping', description='replies with pong!')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"pong! requested by {interaction.user.mention}")

@bot.tree.command(name='spooky', description='scares you!')
async def spooky(interaction: discord.Interaction):
    file = discord.File(os.path.join(os.curdir, 'kanye.jpg'), filename="kanye.jpg")
    await interaction.response.send_message(file=file)

@bot.tree.command(name='play', description='plays a song')
async def search(interaction: discord.Interaction, title: str):

    if interaction.user.voice:
        channel = interaction.user.voice.channel
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if voice == None:
            await channel.connect()
    else:
        interaction.response.send_message("You must be connected to a voice chat first.", ephemeral=True)

    queue.append(title)
    await interaction.response.send_message(f"'{title}' added to the queue!")

    if len(queue) == 1:
        while len(queue) != 0:
            try:
                title = youtubeDl.youtubeAPI(queue[0])
                await interaction.channel.send(f"{title[0]} is now playing.")
            except:
                await interaction.channel.send(f"'{queue[0]}' not found, skipping...")
                queue.pop(0)
                continue
            queue.pop(0)
        
        await discord.utils.get(bot.voice_clients, guild=interaction.guild).disconnect()

    

@bot.tree.command(name='skip', description='skips the current song')
async def skip(interaction: discord.Interaction):
    await interaction.response.send_message()

bot.run(token)