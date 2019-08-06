import discord
import youtube_dl
import os
import re
import common

import googleapiclient.discovery
import googleapiclient.errors

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from discord.ext import commands

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Dictionary of queues for all guilds with a connected voice client
        self.deliberate = False
        self.currentFile = None
        self.check_connections()

        # Options for youtube-dl
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{os.getcwd()}/songs/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        self.ydl = youtube_dl.YoutubeDL(opts)  # youtube-dl object

        print("Loaded music.py")

    def check_connections(self):
        if len(self.bot.voice_clients) != 0:
            for voice_client in self.bot.voice_clients:
                # await voice_client.disconnect()
                print(f"Disconnected from {voice_client.guild}")
        else:
            print("No voice clients detected")

    def end_of_song(self, guild):
        """
        Called at the end of a song.
        Deliberate is a flag for if the song was ended due to a skip_to command.
        """

        if not self.deliberate:
            self.check_queue(guild)

    def check_queue(self, guild):
        print("Checking queue")
        if self.queues[guild.id]:
            voice_client = guild.voice_client

            # Check if ready for next song
            if voice_client.is_connected() and not voice_client.is_playing():
                # Retrieve song information
                song_info = self.queues[guild.id].pop()
                filename = self.ydl.prepare_filename(song_info).split('.')[0] + '.mp3'
                song_url = song_info['webpage_url'];

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

    @commands.command()
    async def play(self, ctx, *args):
        await ctx.message.delete(delay=common.deletion_delay)
        message = " ".join(args)
        url = None

        if re.search(common.youtube_url_regex, message):
            url = message
        else:
            print(f"{message} is not a valid youtube url, assuming search query")
            url = search_youtube(message)

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

        # Validation for non-owners
        if ctx.author.id != common.owner_id:
            if song_info['duration'] > common.max_song_length_seconds:
                await ctx.send(f"Duration of requested song ({song_info['duration']}) exceeds the maximum of "
                               f"{common.max_song_length_seconds / 60} minutes")
                return

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
        if guild.id in self.queues and self.queues[guild.id]:
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


def setup(bot):
    bot.add_cog(Music(bot))


def search_youtube(query: str) -> str:
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_790142580553-q30d3duhu32319jruubhjh6ap7gjfi33.apps.googleusercontent.com.json"

    # Attempt to get existing credentials
    credential_path = os.path.join('./', 'credentials.json')
    store = Storage(credential_path)
    credentials = store.get()

    # Open a browser to get credentials if needed
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)

    # Create Youtube object
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # Youtube API search request
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=query,
        type="video"
    )
    response = request.execute()

    # Grab URL of first video in search results
    url = f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
    return url
