import discord
from discord.ext import commands
from discord.voice_client import VoiceClient


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Called when the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready.")

    # Command for when the user types !ping
    @commands.command()
    async def ping(self, ctx):

        # Reply with the bot's latency
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    @commands.command()
    async def join(self, ctx):
        # Check if author is in a voice channel before connecting
        if ctx.author.voice is None:
            await ctx.send(":x: You must be in a voice channel to use this command")
            return

        guild_client = None  # Reference to the specific server's voice client

        # Check if already connected to a voice channel on the server
        for voiceClient in self.client.voice_clients:
            if voiceClient.guild == ctx.author.guild:
                guild_client = voiceClient
                break

        print(f"Joining {ctx.author.voice.channel}")

        # Join voice channel
        if guild_client is not None:
            await guild_client.move_to(ctx.author.voice.channel)
        else:
            await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        successful = False

        if ctx.author.voice is not None:
            for voiceClient in self.client.voice_clients:
                if voiceClient.channel.id == ctx.author.voice.channel.id:
                    await voiceClient.disconnect()
                    print(f"Leaving {ctx.author.voice.channel}")
                    successful = True

        if not successful:
            await ctx.send(":x: You must be in the same voice channel to use this command")


def setup(client):
    client.add_cog(Commands(client))
