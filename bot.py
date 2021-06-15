import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashCommandOptionType , SlashContext
import mysql.connector

mydb = mysql.connector.connect(
host="localhost",
user="root",
password="m$7a3!W3saC2h@%C8saK",
database="discord_bot",
)

token_file= open("token.txt","r") #create a txt file with the discord bot token inside
token= token_file.read()

client = commands.Bot(command_prefix='!')
slash = SlashCommand(client , sync_commands=True)

@client.event
async def on_ready():
    print("Bot Ready to use :3")
    activity = discord.Game(name="Fais / pour effectuer des commandes", type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)

# options = [
#     {
#         "name": "start",
#         "description" : "Debut la limite du guess",
#         "required" : False,
#         "type" : 4
#     },
#     {
#         "name": "stop",
#         "description" : "Fin de la limite du guess",
#         "required" : False,
#         "type" : 4
#     }
# ]



@slash.slash(description='ça fait prout')
async def hi(ctx : SlashContext):
    await ctx.send("Bonjour ")

@slash.slash(description="Show latency")
async def ping(ctx : SlashContext):
    await ctx.send(f"Bot speed : {round(client.latency *1000)}ms")

@slash.slash(description="Pong comme on dit")
async def test(ctx : SlashContext):
    await ctx.send(f"Wsh wsh wsh <@{ctx.author_id}>")

@slash.slash(description="Ajoute ton ID discord à la BDD")
async def add(ctx : SlashContext):
    cur=mydb.cursor()
    s="INSERT INTO player (ID_DISCORD,Money,XP) VALUES (%s,%s,%s)"
    b1=(ctx.author_id,2,3)
    cur.execute(s,b1)
    mydb.commit()
    await ctx.send(f"C'est bon chacal <@{ctx.author_id}>")

@client.command(pass_contexte=True) #command for run a D20
async def testcommand(ctx):
    cur=mydb.cursor()
    s="INSERT INTO player (ID_DISCORD,Money,XP) VALUES (%s,%s,%s)"
    b1=(ctx.message.author.id,2,3)
    cur.execute(s,b1)
    mydb.commit()
    await ctx.send(f"C'est bon chacal")


client.run(token)
