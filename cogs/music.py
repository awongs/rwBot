import discord
import youtube_dl
import os
import common
from discord.ext import commands


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queues = {}  # Dictionary of queues for all guilds with a connected voice client
        self.deliberate = False
        self.currentFile = None
        self.check_connections()

        opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{os.getcwd()}/songs/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        self.ydl = youtube_dl.YoutubeDL(opts)

        print("Loaded music.py")

    def check_connections(self):
        if len(self.client.voice_clients) != 0:
            for voice_client in self.client.voice_clients:
                # await voice_client.disconnect()
                print(f"Disconnected from {voice_client.guild}")
        else:
            print("No voice clients detected")

    def check_queue(self, guild):
        print("Checking queue")
        if self.queues[guild.id]:
            voice_client = guild.voice_client

            # Check if ready for next song
            if voice_client.is_connected() and not voice_client.is_playing():
                # Retrieve song information
                song_info = self.queues[guild.id].pop()
                filename = self.ydl.prepare_filename(song_info).split('.')[0] + '.mp3'
                song_url = song_info["webpage_url"];

                self.currentFile = filename

                # Download the song if this is the first time playing it
                if not os.path.exists(filename):
                    self.ydl.download([song_url])

                # Create and play audio source
                audio_source = discord.FFmpegPCMAudio(filename)

                print(f"Now playing in {voice_client.channel.name} - {song_info['title']}")

                voice_client.play(audio_source, after=lambda e: self.end_of_song(guild))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 0.15

        else:
            print("Queue is empty")

    def end_of_song(self, guild):
        if not self.deliberate:
            self.check_queue(guild)

    @commands.command()
    async def play(self, ctx, url):
        await ctx.message.delete(delay=common.deletion_delay)

        # Reference to the specific server's voice client
        guild = ctx.author.guild
        voice_client = guild.voice_client

        # Connect to the author's channel
        if voice_client is None:
            voice_client = await ctx.author.voice.channel.connect()
        elif voice_client.channel.id != ctx.author.voice.channel.id:
            await ctx.send(":x: You must be in the same voice channel to use this command")

        # Get song information
        song_info = self.ydl.extract_info(url, download=False)

        # Add song to the queue
        if guild.id in self.queues:
            self.queues[guild.id].append(song_info)
        else:
            self.queues[guild.id] = [song_info]

        position_in_queue = len(self.queues[guild.id])
        await ctx.send(f"Queued {song_info['title']} - {song_info['webpage_url']} "
                       f" | Position in Queue: {position_in_queue}")

        # Check queue here if bot is idle
        if not voice_client.is_playing():
            self.check_queue(guild)

    @commands.command(aliases=["skipto"])
    async def skip_to(self, ctx, time):
        await ctx.message.delete(delay=common.deletion_delay)

        guild = ctx.author.guild
        voice_client = guild.voice_client

        self.deliberate = True  # Set flag

        voice_client.stop()

        # Create and play audio source, skip to input time
        audio_source = discord.FFmpegPCMAudio(self.currentFile, before_options=f"-ss {time}")

        voice_client.play(audio_source, after=lambda e: self.end_of_song(guild))
        voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
        voice_client.source.volume = 0.15

        self.deliberate = False  # Reset flag

    @commands.command()
    async def stop(self, ctx):
        await ctx.message.delete(delay=common.deletion_delay)

        guild = ctx.author.guild
        voice_client = guild.voice_client
        voice_client.stop()

    @commands.command()
    async def queue(self, ctx):
        await ctx.message.delete(delay=common.deletion_delay)

        # Reference to the author's guild
        guild = ctx.author.guild

        # Display queue
        if guild.id in self.queues:
            message = ""
            for num, song_info in enumerate(self.queues[guild.id], start=1):
                message += f"{num}: {song_info['title']}\n"

            await ctx.send(message)
        else:
            await ctx.send("Queue is currently empty.")

    @commands.command()
    async def skip(self, ctx):
        await ctx.message.delete(delay=common.deletion_delay)

        # Reference to the specific server's voice client
        guild = ctx.author.guild
        voice_client = guild.voice_client

        if voice_client is not None and voice_client.channel.id == ctx.author.voice.channel.id:
            if voice_client.is_playing():
                voice_client.stop()
        else:
            await ctx.send(":x: You must be in the same voice channel to use this command")


def setup(client):
    client.add_cog(Music(client))
