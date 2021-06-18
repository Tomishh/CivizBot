from asyncio.windows_events import NULL
from inspect import getfullargspec
import discord
from discord.ext import commands
from discord.flags import Intents
from discord_slash import SlashCommand, SlashCommandOptionType , SlashContext
import mysql.connector
import csv
import time

list=[]

with open('ConnectionString.csv','r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader :
        list.append(row)
    mydb = mysql.connector.connect(
    host=list[0][0],
    user=list[1][0],
    password=list[2][0],
    database=list[3][0],
    )

token_file= open("token.txt","r") #create a txt file with the discord bot token inside
token= token_file.read()

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!',intents=intents)
slash = SlashCommand(client , sync_commands=True)

guild_ids = [543518985145024522] 

def progress_bar(n):
    full="█"
    empty="░"
    string=""
    for i in range(10-n):
        string=f"{string}{full}"
    for j in range(n):
        string=f"{string}{empty}"
    return string

def get_level_xp(level):
    return (5*(level*level)+(50*level)+100)

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
    discord_id = cur.fetchall()
    print(discord_id)
    if discord_id == []:
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
        cur=mydb.cursor()
        query_timestamp=f"select last_message from player where ID_Discord = {message.author.id}"
        cur.execute(query_timestamp)
        last_message=cur.fetchall()
        last_message_delay=last_message[0][0]+3
        actual_time=int(time.time())
        print(f"message send by {message.author}")
        query_getplayerlevel = f"select level from player where ID_Discord = {message.author.id}"
        cur.execute(query_getplayerlevel)
        player_level=cur.fetchall()
        if last_message_delay<actual_time:
            #   AJOUT DE L'XP ET DE L'ARGENT
            query_addxp=f"update player set XP =(SELECT XP WHERE ID_Discord='{message.author.id}')+5, last_message='{actual_time}' where ID_Discord='{message.author.id}'"
            cur.execute(query_addxp)
            print(f"{message.author} XP added and last_message updated\n")
            mydb.commit()
            query_get_player_xp = f"SELECT XP from player WHERE ID_Discord='{message.author.id}'"
            cur.execute(query_get_player_xp)
            player_xp=cur.fetchall()
            query_get_player_level = f"SELECT level from player WHERE ID_Discord='{message.author.id}'"
            cur.execute(query_get_player_level)
            player_level_temp=cur.fetchall()
            player_level=player_level_temp[0][0]
            needed_xp = (5*(player_level*player_level)+(50*player_level)+100)
            if player_xp[0][0] > needed_xp:
                query_levelup= f"update player set level =(SELECT level WHERE ID_Discord='{message.author.id}')+1 where ID_Discord='{message.author.id}'"
                cur.execute(query_levelup)
                mydb.commit()
                player_level_add = player_level + 1
                await message.channel.send(f"<@{message.author.id}> a Level-up ! Tu es passé niveau {player_level_add}")
                print(f"{message.author} level up !")
        else:
            print("Message sended too early to add XP")




# # options = [
# #     {
# #         "name": "start",
# #         "description" : "Debut la limite du guess",
# #         "required" : False,
# #         "type" : 4
# #     },
# #     {a

# #         "name": "stop",
# #         "description" : "Fin de la limite du guess",
# #         "required" : False,
# #         "type" : 4
# #     }
# # ]



@slash.slash(description='ça fait prout')
async def hi(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send("Bonjour mon reuf 3")

@slash.slash(description="Show latency")
async def ping(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send(f"Bot speed : {round(client.latency *1000)}ms")

@slash.slash(description="Pong comme on dit")
async def test(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send(f"Wsh wsh wsh <@{ctx.author_id}>")

@slash.slash(description="Ajoute ton ID discord à la BDD")
async def add(ctx : SlashContext,guild_ids=guild_ids):
    cur=mydb.cursor()
    s="INSERT INTO player (ID_DISCORD,Money,XP) VALUES (%s,%s,%s)"
    b1=(ctx.author_id,2,3)
    cur.execute(s,b1)
    mydb.commit()
    await ctx.send(f"C'est bon chacal <@{ctx.author_id}>")

@slash.slash(description="Montre ton XP")
async def level(ctx : SlashContext, guild_ids=guild_ids):
    cur=mydb.cursor()
    s=f"select level,XP from player where ID_Discord={ctx.author_id}"
    cur.execute(s)
    value=cur.fetchall()
    level=value[0][0]
    XP_player=value[0][1]
    XP_needed = get_level_xp(level)-XP_player
    level_xp=get_level_xp(level)-get_level_xp(level-1)
    #arrondir de [0;10] la progression d'XP
    XP_player_10 = ((10*XP_needed)/level_xp)
    int_xp_10=int(XP_player_10)
    XP_progress = level_xp-XP_needed
    await ctx.send(f"Niveau : {level}   {progress_bar(int_xp_10)}  {XP_progress}/{level_xp}")
    



client.run(token)
