import requests, yt_dlp
import os

class NotFoundError(Exception):
    pass

API_KEY = 'AIzaSyCrDaYeqhE9JzbSUS3ALlJgexjGrRCf5w4'

# Options for yt-dlp


def findSong(keyword: str):
    apiUrl = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={keyword}&key={API_KEY}'
    data = requests.get(apiUrl).json()

    if not data["items"]: raise NotFoundError()

    videoTitle = data["items"][0]['snippet']['title']

    return videoTitle

def youtubeAPI(keyword: str):
    apiUrl = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={keyword}&key={API_KEY}'
    data = requests.get(apiUrl).json()

    if not data["items"]: raise NotFoundError()

    videoId = data["items"][0]['id']['videoId']
    videoTitle = data["items"][0]['snippet']['title']

    url, errExtension = downloadAudio(videoId=videoId, title=videoTitle)
    return url, videoTitle + errExtension + '.mp3'

def downloadAudio(videoId: str, title:str) -> tuple[str, str]: #remember to add ffmpeg to the system enviroment variables
    videoUrl = f"https://www.youtube.com/watch?v={videoId}"

    errExtension = ''
    ydl_opts = {
    'format': 'bestaudio/best',  # Select best audio format available
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',  # Extract audio
        'preferredcodec': 'mp3',  # Convert to MP3
        'preferredquality': '192',  # Set bitrate to 192 kbps
    }],
    'outtmpl': f'{title}',  # Output filename
    #'quiet': True,  # Suppress console output
    #'force_overwrite': True,  # Overwrite existing files
    }
    
    # Download the audio
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoUrl])
    except:
        ydl_opts['outtmpl'] = f'{title}err'
        errExtension = 'err'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoUrl])
    
    return videoUrl, errExtension

def clean(file: str):
    os.remove(file)