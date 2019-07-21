import discord
import youtube_dl
import os
from discord.ext import commands


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Loaded music.py")

    @commands.command()
    async def play(self, ctx, url):

        # Reference to the specific server's voice client
        voice_client = ctx.author.guild.voice_client
        
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

            voice_client.play(discord.FFmpegPCMAudio(filename), after=lambda e: print('done', e))
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.15
            print(f"Playing - {filename}")


def setup(client):
    client.add_cog(Music(client))
