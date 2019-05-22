import discord
from discord.ext import commands
from discord.voice_client import VoiceClient


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.voiceClient = None

    # Called when the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready.")

    # Command for when the user types !ping or !ozma
    @commands.command()
    async def ping(self, ctx):

        # Reply with the bot's latency
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    @commands.command()
    async def join(self, ctx):

        # Check if author is in a voice channel before connecting
        if ctx.author.voice is not None:
            print(f"Joining {ctx.author.voice.channel}")
            self.voiceClient = await ctx.author.voice.channel.connect()  # Join voice channel

    @commands.command()
    async def leave(self, ctx):

        if self.voiceClient is not None and self.voiceClient.is_connected():
            print("Left channel")
            await self.voiceClient.disconnect()
        else:
            print("Not in a channel")


def setup(client):
    client.add_cog(Commands(client))
