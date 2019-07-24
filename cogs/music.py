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
        if not self.queues[guild.id]:
            voice_client = guild.voice_client

            # Check if ready for next song
            if voice_client.is_connected() and not voice_client.is_playing():
                audio_source = self.queues[guild.id].pop()
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

        if voice_client is not None:

            opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{os.getcwd()}/songs/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with youtube_dl.YoutubeDL(opts) as ydl:
                song_info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(song_info).split('.')[0] + '.mp3'

            audio_source = discord.FFmpegPCMAudio(filename)

            if guild.id in self.queues:
                self.queues[guild.id].append(audio_source)
            else:
                self.queues[guild.id] = [audio_source]
            await ctx.send(f"Queued {filename}.")

            self.check_queue(guild)

            #voice_client.play(audio_source, after=lambda e: print('done', e))
            #voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            #voice_client.source.volume = 0.15
            #print(f"Playing - {filename}")

    @commands.command()
    async def skip(self, ctx):

        # Reference to the specific server's voice client
        guild = ctx.author.guild
        voice_client = guild.voice_client

        if voice_client is not None and voice_client.is_playing():
            voice_client.stop()


def setup(client):
    client.add_cog(Music(client))
