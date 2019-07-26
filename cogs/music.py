import discord
import youtube_dl
import os
from discord.ext import commands


class Music(commands.Cog):

    # Dictionary of queues for all guilds with a connected voice client
    queues = {}

    def __init__(self, client):
        self.client = client
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

                # Download the song if this is the first time playing it
                if not os.path.exists(filename):
                    self.ydl.download([song_url])

                # Create and play audio source
                audio_source = discord.FFmpegPCMAudio(filename)

                print(f"Now playing in {voice_client.channel.name} - {song_info['title']}")

                voice_client.play(audio_source, after=lambda e: self.check_queue(guild))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 0.15

        else:
            print("Queue is empty")

    @commands.command()
    async def play(self, ctx, url):

        # Reference to the specific server's voice client
        guild = ctx.author.guild
        voice_client = guild.voice_client

        # Connect to the author's channel
        if voice_client is None:
            voice_client = await ctx.author.voice.channel.connect()
        else:
            await voice_client.move_to(ctx.author.voice.channel)

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

    @commands.command()
    async def skip(self, ctx):

        # Reference to the specific server's voice client
        guild = ctx.author.guild
        voice_client = guild.voice_client

        if voice_client is not None and voice_client.is_playing():
            voice_client.stop()


def setup(client):
    client.add_cog(Music(client))
