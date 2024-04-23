import discord, os, youtubeDl
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio
from musicInstance import musicInstance

token = open('token.txt', 'r').readline()

instances = dict()
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)

ffmpegPath = "C:\\Users\\Marco\\Downloads\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"
queue = []
cleanQueue = []

@bot.event #gli eventi hanno questo decoratore
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.activity.CustomActivity(name="listening to youtube"))
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
    await interaction.response.defer()

    if not interaction.guild_id in instances:
        if interaction.user.voice:
            instances[interaction.guild_id] = musicInstance(guild_id=interaction.guild_id, bot=bot, voiceChannel=interaction.user.voice.channel, voiceClient=await interaction.user.voice.channel.connect(), channel=interaction.channel)
            queueing = False
        else:
            await interaction.followup.send("You must be connected to a voice chat first.", ephemeral=True)
            return
    else:
        queueing = True
    
    curr = instances[interaction.guild_id]
    await interaction.followup.send(f"**{curr.addToQueue(title)}** added to the queue!")

    if not queueing:
        curr.play_Song()
    

@bot.tree.command(name='skip', description='skips the current song')
async def skip(interaction: discord.Interaction):
    if interaction.user.voice:
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if not voice:
            await interaction.response.send_message("In order to skip the bot must be connected to a channel.", ephemeral=True)
            return
        
        if interaction.user.voice.channel == instances[interaction.guild_id].voiceChannel:
            instances[interaction.guild_id].vc.stop()
            await interaction.response.send_message("Song skipped.")
        else:
            await interaction.response.send_message("In order to skip you must be connected to the same channel as the bot.", ephemeral=True)
    else:
        await interaction.response.send_message("In order to skip you must be connected to the same channel as the bot.", ephemeral=True)
    
bot.run(token)