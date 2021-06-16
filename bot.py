from asyncio.windows_events import NULL
import discord
from discord.ext import commands
from discord.flags import Intents
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

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!cvz',intents=intents)
slash = SlashCommand(client , sync_commands=True)

@client.event
async def on_ready():
    print("Bot Ready to use")
    activity = discord.Game(name="Fais / pour effectuer des commandes", type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)

@client.event
async def on_member_join(member):
    await member.send("Hello, bienvenue ma couille")
    query_if_exist = f"select ID_Discord From Player Where ID_Discord = '{member.id}'"
    cur=mydb.cursor()
    cur.execute(query_if_exist)
    presence = cur.fetchall()
    print(presence)
    if presence == []:
        query=f"insert into player (ID_Discord,Money,XP,last_message) VALUES ('{member.id}','0','0','0')"
        cursor=mydb.cursor()
        cursor.execute(query)
        mydb.commit()
        print(f"{member} added at the database")
    else :
        print(f"Member {member} Already existe inside the Database")
        


@client.event
async def on_message(message):
    if not message.author.bot:
        print(f"message send by {message.author}")
        cur=mydb.cursor()
        query=f"update player set XP =(SELECT XP WHERE ID_Discord='{message.author.id}')+10 where ID_Discord='{message.author.id}'"
        cur.execute(query)
        mydb.commit()
        print(f"{message.author} XP added")




# # options = [
# #     {
# #         "name": "start",
# #         "description" : "Debut la limite du guess",
# #         "required" : False,
# #         "type" : 4
# #     },
# #     {
# #         "name": "stop",
# #         "description" : "Fin de la limite du guess",
# #         "required" : False,
# #         "type" : 4
# #     }
# # ]



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

@client.command(pass_contexte=True)
async def testcommand(ctx):
    cur=mydb.cursor()
    s="INSERT INTO player (ID_DISCORD,Money,XP) VALUES (%s,%s,%s)"
    b1=(ctx.message.author.id,2,3)
    cur.execute(s,b1)
    mydb.commit()
    await ctx.send(f"C'est bon chacal")


client.run(token)
