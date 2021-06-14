import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashCommandOptionType , SlashContext
import random

token_file= open("token.txt","r") #create a txt file with the discord bot token inside
token= token_file.read()

client = commands.Bot(command_prefix='!')
slash = SlashCommand(client , sync_commands=True)

@client.event
async def on_ready():
    print("Bot Ready to use :3")

options = [
    {
        "name": "start",
        "description" : "Debut la limite du guess",
        "required" : False,
        "type" : 4
    },
    {
        "name": "stop",
        "description" : "Fin de la limite du guess",
        "required" : False,
        "type" : 4
    }
]

@slash.slash(name= 'Hi' , description='Dit bonjour')
async def guess(ctx : SlashContext):
    await ctx.send("Bonjour")


client.run(token)
