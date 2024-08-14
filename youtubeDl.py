import requests, yt_dlp, dotenv
import os, discord

class NotFoundError(Exception):
    pass

DIR = 'downloads/'

if not os.path.exists('downloads'): os.mkdir('downloads')

def findSong(keyword: str):
    ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1',
            'quiet': True,
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(keyword, download=False)
        
        videoTitle = data['entries'][0]['title']

    return videoTitle

def downloadAudio(keyword: str, guild_id: discord.interactions.Interaction.guild_id) -> tuple[str, str]: #remember to add ffmpeg to the system enviroment variables
    filename = f'{hex(int.from_bytes(keyword.encode())%(1<<42)).replace("0x", "")}'
    ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1',
            'outtmpl': os.path.join(f'{DIR}{filename}-{guild_id}'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
        }
    
    errExtension = ''
    # Download the audio
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(keyword, download=True)
            print(data['entries'][0]['original_url'])
    except:
        ydl_opts['outtmpl'] = f'{DIR}{filename}err-{guild_id}'
        errExtension = 'err'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(keyword, download=True)
    
    return data['entries'][0]['original_url'], f'{DIR}{filename}{errExtension}-{guild_id}.mp3'

def clean(file: str):
    if os.path.exists(file):
        os.remove(file)