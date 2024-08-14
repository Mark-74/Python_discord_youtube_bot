import discord, youtubeDl, asyncio
from discord.ext import commands

class musicInstance:
    def __init__(self, bot: commands.bot, guild_id: discord.interactions.Interaction.guild_id, voiceChannel: discord.VoiceChannel, voiceClient: discord.VoiceClient, channel: discord.channel, cleanQueue = []) -> None:
        self.guild_id = guild_id    #guild of the current bot instance
        self.channel = channel      #channel used to display ongoing songs
        self.voiceChannel = voiceChannel
        self.vc = voiceClient       #active connection to a channel
        self.queue = []
        self.cleanQueue = cleanQueue
        self.bot = bot
        
    class View(discord.ui.View):
        class SkipButton(discord.ui.Button):
            def __init__(self, instance):
                super().__init__(style=discord.ButtonStyle.secondary, emoji='⏩', custom_id="skip")
                self.instance = instance
            
            async def callback(self, interaction: discord.Interaction):
                await self.instance.skip()
                await interaction.response.send_message("Skipping the current song.", ephemeral=True)
        
        class QueueButton(discord.ui.Button):
            def __init__(self, instance):
                super().__init__(style=discord.ButtonStyle.green, emoji='🚦', custom_id="queue")
                self.instance = instance
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(content=self.instance.listQueue())
        
        class StopButton(discord.ui.Button):
            def __init__(self, instance):
                super().__init__(style=discord.ButtonStyle.red, emoji="⛔", custom_id="stop")
                self.instance = instance
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message("Bot disconnected.", ephemeral=True)
                await self.instance.stop()
        
        class PauseButton(discord.ui.Button):
            def __init__(self, instance):
                super().__init__(style=discord.ButtonStyle.blurple, emoji="⏸️", custom_id="pause")
                self.instance = instance
            
            async def callback(self, interaction: discord.Interaction):
                if self.instance.vc.is_playing(): 
                    self.instance.vc.pause()
                    await interaction.response.send_message("Pausing the current song.", ephemeral=True)
                else:
                    await interaction.response.send_message("The song is already paused.", ephemeral=True)
        
        class ResumeButton(discord.ui.Button):
            def __init__(self, instance):
                super().__init__(style=discord.ButtonStyle.blurple, emoji="▶️", custom_id="resume")
                self.instance = instance
            
            async def callback(self, interaction: discord.Interaction):
                if self.instance.vc.is_paused():
                    self.instance.vc.resume()
                    await interaction.response.send_message("Resuming the current song.", ephemeral=True)
                else:
                    await interaction.response.send_message("The song is already playing.", ephemeral=True)
        
        def __init__(self, instance):
            super().__init__(timeout=None)
            self.add_item(self.QueueButton(instance))
            self.add_item(self.SkipButton(instance))
            self.add_item(self.StopButton(instance))
            self.add_item(self.PauseButton(instance))
            self.add_item(self.ResumeButton(instance))
    
    async def play_Song(self) -> None:
        if len(self.queue) > 0:
            #clean old song files
            if len(self.cleanQueue) >= 2: self.clean()

            try: #download song
                result = youtubeDl.youtubeAPI(keyword=self.queue.pop(0), guild_id=self.guild_id)
            except Exception as e: #song not found
                if len(self.queue) > 0: await self.channel.send(content="Song not found, moving on to the next.")
                else: await self.channel.send(content="Song not found")
                await self.next_Song()
                return

            #play song
            self.cleanQueue.append(result[1])
            message = await self.channel.send(content=f"Now playing **{result[0]}**", view=self.View(instance=self))
            self.vc.play(discord.FFmpegPCMAudio(source=result[1]), after = lambda e: asyncio.run_coroutine_threadsafe(self.next_Song(last=message), self.bot.loop))

        else: await self.vc.disconnect()

    async def next_Song(self, last: discord.Message=None) -> None:
        if last:
            await last.delete()
        #check for new song to play
        if len(self.queue) > 0:
            #clean old song files
            if len(self.cleanQueue) >= 2: self.clean()

            try: #download song
                msg = await self.channel.send("Moving on to the next.")
                result = youtubeDl.youtubeAPI(keyword=self.queue.pop(0), guild_id=self.guild_id)
            except: #song not found
                if len(self.queue) > 0: await msg.edit(content="Song not found, moving on to the next.")
                else: await msg.edit(content="Song not found")
                await self.next_Song()
                return

            #play song
            self.cleanQueue.append(result[1])
            message = await msg.edit(content=f"Now playing **{result[0]}**", view=self.View(instance=self))
            self.vc.play(discord.FFmpegPCMAudio(source=result[1]), after = lambda e: asyncio.run_coroutine_threadsafe(self.next_Song(last=message), self.bot.loop))

        else: await self.vc.disconnect()
    
    async def skip(self) -> None:
        if self.vc.is_playing(): self.vc.stop()
        
    async def stop(self) -> None:
        self.queue.clear()
        self.vc.stop()
        await self.vc.disconnect(force=True)
    
    def clean(self):
        youtubeDl.clean(self.cleanQueue.pop(0))

    def addToQueue(self, title: str) -> str:
        self.queue.append(title)
        try:
            return youtubeDl.findSong(title)
        except:
            return title
    
    def listQueue(self) -> str:
        result = ""
        
        for song in self.queue:
            result += f"**{song}**\n"
        
        if result == "": result = "No songs in queue."
        return result
