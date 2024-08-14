import requests, yt_dlp, dotenv
import os, discord

class NotFoundError(Exception):
    pass

dotenv.load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
DIR = 'downloads/'

if not os.path.exists('downloads'): os.mkdir('downloads')

# Options for yt-dlp


def findSong(keyword: str):
    apiUrl = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={keyword}&key={API_KEY}'
    data = requests.get(apiUrl).json()

    if not data["items"]: raise NotFoundError()

    videoTitle = data["items"][0]['snippet']['title']

    return videoTitle

def youtubeAPI(keyword: str, guild_id="1234") -> tuple[str, str]:
    apiUrl = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={keyword}&key={API_KEY}'
    data = requests.get(apiUrl).json()

    if not data["items"]: raise NotFoundError()

    videoId = data["items"][0]['id']['videoId']
    videoTitle = data["items"][0]['snippet']['title']

    url, errExtension = downloadAudio(videoId=videoId, title=videoTitle, guild_id=guild_id)
    return url, f"{DIR}{videoTitle}{errExtension}-{guild_id}.mp3"

def downloadAudio(videoId: str, title:str, guild_id: discord.interactions.Interaction.guild_id) -> tuple[str, str]: #remember to add ffmpeg to the system enviroment variables
    videoUrl = f"https://www.youtube.com/watch?v={videoId}"

    errExtension = ''
    ydl_opts = {
    'format': 'bestaudio/best',  # Select best audio format available
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',  # Extract audio
        'preferredcodec': 'mp3',  # Convert to MP3
        'preferredquality': '192',  # Set bitrate to 192 kbps
    }],
    'outtmpl': f'{DIR}{title}-{guild_id}',  # Output filename
    #'quiet': True,  # Suppress console output
    #'force_overwrite': True,  # Overwrite existing files
    }
    
    # Download the audio
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoUrl])
    except:
        ydl_opts['outtmpl'] = f'{DIR}{title}err-{guild_id}'
        errExtension = 'err'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoUrl])
    
    return videoUrl, errExtension

def clean(file: str):
    os.remove(file)