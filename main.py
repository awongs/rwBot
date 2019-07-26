import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix='.')


# Called when the bot is ready
@client.event
async def on_ready():
    print("Bot is ready.")


@client.listen()
async def on_message(msg):
    # Delete bot messages after a delay
    if msg.author == client.user:
        await msg.delete(delay=10)

    print(f"{msg.author}: {msg.content}  ---  {msg.author.guild}.{msg.channel}")  # Logging


@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

# Run the bot, hardcoded token for now
client.run("MzUzODI2MDgwNjc2OTA0OTYw.XON2JA.JaeuYU_6J70IwgRyTrQI47cHClI")
