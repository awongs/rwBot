import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    print("Bot is ready.")


client.run("MzUzODI2MDgwNjc2OTA0OTYw.XON2JA.JaeuYU_6J70IwgRyTrQI47cHClI")