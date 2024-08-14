# Youtube music bot - Python 

## Features
- Multi-Server
the bot can play music in multiple servers at the same time.
- Button interface
buttons are present to manage the current song.
- Downloaded files cleaning
there is a cleaning queue for the downloaded files that keeps saved only 2 files per server at any moment.
- Youtube research
thanks to youtube's api it's possible to research for songs directly from youtube.

## API
The bot depends on youtube's api for researching songs and on yt_dlp's api to download them.

## Class management
- MusicInstance
manages every instance of the bot in each servers in which it's added, it contains the logic responsible for the music playing and for the queue management, furthermore it uses the nex class to clean the downloaded files.
- YoutubeDL
not a class, but but a group of useful functions to manage the downloaded files.
