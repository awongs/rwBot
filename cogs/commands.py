import discord
import common
from discord.ext import commands


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("Loaded commands.py")

    # Command for when the user types !ping
    @commands.command()
    async def ping(self, ctx):

        # Reply with the bot's latency
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @commands.command()
    async def summon(self, ctx):
        await ctx.message.delete(delay=common.deletion_delay)

        # Check if author is in a voice channel before connecting
        if ctx.author.voice is None:
            await ctx.send(":x: You must be in a voice channel to use this command")
            return

        # Reference to the specific server's voice client
        voice_client = ctx.author.guild.voice_client

        print(f"Joining {ctx.author.voice.channel}")

        # Join voice channel
        if voice_client is not None and voice_client.channel.id != ctx.author.voice.channel.id:
            await voice_client.move_to(ctx.author.voice.channel)
        else:
            await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        await ctx.message.delete(delay=common.deletion_delay)

        # Reference to the specific server's voice client
        voice_client = ctx.author.guild.voice_client

        # Check if the message author is in the same voice channel
        if voice_client is not None and voice_client.channel.id == ctx.author.voice.channel.id:

            # Leave voice channel
            await voice_client.disconnect()
            print(f"Leaving {ctx.author.voice.channel}")
        else:
            await ctx.send(":x: You must be in the same voice channel to use this command")


def setup(bot):
    bot.add_cog(Commands(bot))
