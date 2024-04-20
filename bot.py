import discord, os, youtubeDl
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio

token = open('token.txt', 'r').readline()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)

ffmpegPath = "C:\\Users\\Marco\\Downloads\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"
queue = []
cleanQueue = []

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
    await interaction.response.defer()

    if interaction.user.voice:
        channel = interaction.user.voice.channel
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if voice == None:
            queueing = False
            vc = await channel.connect()
        else: queueing = True
    else:
        await interaction.followup.send("You must be connected to a voice chat first.", ephemeral=True)
        return
    
    #adding song to queue
    queue.append(title)
    await interaction.followup.send(f"**{youtubeDl.findSong(title)}** added to the queue!")

    def after_playing(interaction: discord.Interaction, vc: discord.VoiceClient):
        if len(cleanQueue) >= 2:
            youtubeDl.clean(cleanQueue.pop(0))
            
        if len(queue) > 0:
            msg = asyncio.run_coroutine_threadsafe(interaction.channel.send("Song finished, moving on to the next."), bot.loop).result()
            try:
                title = youtubeDl.youtubeAPI(queue.pop(0))
            except:
                after_playing(interaction=interaction, vc=vc)
                return
            
            cleanQueue.append(title[1])
            asyncio.run_coroutine_threadsafe(msg.edit(content=f"{title[0]} is now playing."), bot.loop)
            vc.play(discord.FFmpegPCMAudio(source=title[1]), after = lambda e: after_playing(interaction=interaction, vc=vc))

        else:
            asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop)

    #starting player if it wasn't in the vc
    if not queueing:
        try: title = youtubeDl.youtubeAPI(queue.pop(0))
        except: 
            await interaction.channel.send("Not found.")
            vc.disconnect()
            return
        
        await interaction.channel.send(f"{title[0]} is now playing.")
        cleanQueue.append(title[1])
        vc.play(discord.FFmpegPCMAudio(source=title[1]), after = lambda e: after_playing(interaction=interaction, vc=vc, previousSongFile=title[1]))

    

@bot.tree.command(name='skip', description='skips the current song')
async def skip(interaction: discord.Interaction):
    if interaction.user.voice:
        voice = discord.utils.get(bot.voice_clients, guild=interaction.guild)

        if not voice:
            await interaction.response.send_message("In order to skip the bot must be connected to a channel.", ephemeral=True)
            return
        
        if interaction.user.voice.channel == voice.channel:
            vc = interaction.guild.voice_client
            vc.stop()
            await interaction.response.send_message("Song skipped.")
        else:
            await interaction.response.send_message("In order to skip you must be connected to the same channel as the bot.", ephemeral=True)
    else:
        await interaction.response.send_message("In order to skip you must be connected to the same channel as the bot.", ephemeral=True)
    

bot.run(token)