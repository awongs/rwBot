import discord
import youtube_dl
import os
from discord.ext import commands


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Loaded music.py")

    # Get's the voice client that is connected to the author's server
    def get_voice_client(self, author_guild: discord.Guild) -> discord.VoiceClient:
        for voice_client in self.client.voice_clients:
            if voice_client.guild == author_guild:
                return voice_client

        return None

    @commands.command()
    async def play(self, ctx, url):

        # Reference to the specific server's voice client
        voice_client = self.get_voice_client(author_guild=ctx.author.guild)

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
                song_info = ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=True)
                filename = ydl.prepare_filename(song_info)[:-5] + ".mp3"

            voice_client.play(discord.FFmpegPCMAudio(filename), after=lambda e: print('done', e))
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 0.15


def setup(client):
    client.add_cog(Music(client))