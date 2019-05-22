import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix = '!')


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