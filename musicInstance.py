import discord, youtubeDl

class musicInstance:
    def __init__(self, guild_id: discord.interactions.Interaction.guild_id, voiceClient: discord.VoiceClient, channel: discord.channel) -> None:
        self.guild_id = guild_id    #guild of the current bot instance
        self.channel = channel      #channel used to display ongoing songs
        self.vc = voiceClient       #active connection to a channel
        self.queue = []
        self.cleanQueue = []
    
    async def play_Song(self) -> None:
        if len(self.queue) > 0:
            #clean old song files
            if len(self.cleanQueue) >= 2: self.clean()

            try: #download song
                result = youtubeDl.youtubeAPI(keyword=self.queue.pop(0), guild_id=self.guild_id)
            except: #song not found
                if len(self.queue) > 0: await self.channel.send(content="Song not found, moving on to the next.")    
                self.next_Song()
                return

            #play song
            self.cleanQueue.append(result[1])
            await self.channel.send(content=f"Now playing **{result[0]}**")
            self.vc.play(discord.FFmpegPCMAudio(source=result[1]), after = lambda e: self.next_Song())

        else: await self.vc.disconnect()

    async def next_Song(self) -> None:
        #check for new song to play
        if len(self.queue) > 0:
            #clean old song files
            if len(self.cleanQueue) >= 2: self.clean()

            try: #download song
                msg = await self.channel.send("Song finished, moving on to the next.")
                result = youtubeDl.youtubeAPI(keyword=self.queue.pop(0), guild_id=self.guild_id)
            except: #song not found
                if len(self.queue) > 0: await msg.edit(content="Song not found, moving on to the next.")    
                self.next_Song()
                return

            #play song
            self.cleanQueue.append(result[1])
            await msg.edit(content=f"Now playing **{result[0]}**")
            self.vc.play(discord.FFmpegPCMAudio(source=result[1]), after = lambda e: self.next_Song())

        else: await self.vc.disconnect()
    
    async def skip(self) -> None:
        if self.vc.is_playing(): self.vc.stop()
    
    def clean(self):
        youtubeDl.clean(self.cleanQueue.pop(0))