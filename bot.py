from asyncio.windows_events import NULL
from configparser import DEFAULTSECT
from inspect import getfullargspec
import discord
from discord import embeds
from discord.ext import commands
from discord.flags import Intents
from discord_slash import SlashCommand, SlashCommandOptionType , SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import mysql.connector
import csv
import time


# Import external files :
import global_function


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

@client.event
async def on_ready():
    print("Bot Ready to use")
    activity = discord.Game(name="Fais / pour effectuer des commandes", type=3)
    
@client.event
async def on_member_join(member):
    await member.send("Hello, bienvenue ma couille")
    query_if_exist = f"select ID_Discord From Player Where ID_Discord = '{member.id}'"
    cur=mydb.cursor()
    cur.execute(query_if_exist)
    discord_id = cur.fetchall()
    print(discord_id)
    if discord_id == []:
        query=f"insert into player (ID_Discord,Money,XP,last_message,level) VALUES ('{member.id}','0','0','0','1')"
        cursor=mydb.cursor()
        cursor.execute(query)
        mydb.commit()
        print(f"{member} added at the database")
    else :
        print(f"Member {member} Already existe inside the Database")

@client.event
async def on_message(message):
    if not message.author.bot:
        last_message_delay=global_function.get_player_last_message(message.author.id)+20
        actual_time=int(time.time())
        if last_message_delay<actual_time: #   AJOUT DE L'XP ET DE L'ARGENT
            cur=mydb.cursor()
            query_addxp=f"update player set XP ={global_function.get_player_xp(message.author.id)+3},money='{global_function.get_player_money(message.author.id)+5}', last_message='{actual_time}' where ID_Discord='{message.author.id}'"
            cur.execute(query_addxp)
            print(f"{message.author} XP added and last_message updated")
            mydb.commit()
            needed_xp = (5*(global_function.get_player_level(message.author.id)**2)+(50*global_function.get_player_level(message.author.id))+100)
            if global_function.get_player_xp(message.author.id) > needed_xp:
                await message.channel.send(f"<@{message.author.id}> a Level-up ! Tu es passé niveau {global_function.get_player_level(message.author.id)+1}")
                query_levelup= f"update player set level =(SELECT level WHERE ID_Discord='{message.author.id}')+1 where ID_Discord='{message.author.id}'"
                cur.execute(query_levelup)
                mydb.commit()
                
                print(f"{message.author} level up !")
        else:
            print(f"Message sended too early by {message.author} to add XP")

@slash.slash(guild_ids=guild_ids,description='ça fait prout')
async def hi(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send("Bonjour mon reuf 3")

@slash.slash(guild_ids=guild_ids,description="Show latency")
async def ping(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send(f"Bot speed : {round(client.latency *1000)}ms")

@slash.slash(guild_ids=guild_ids,description="Pong comme on dit")
async def test2(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send(f"Wsh wsh wsh <@{ctx.author_id}>")

@slash.slash(guild_ids=guild_ids,name="useraddDB", description="ajoute utilisateur a la bdd", options=[
{   "name": "user",
    "description": "Sélectionne l'utilisateur à ajouter à la BDD",
    "type": 6,
    "required": "true"
    },])

async def useraddDB(ctx : SlashContext,user, guild_ids=guild_ids):
    cur=mydb.cursor()
    query_add_user=f"insert into player (ID_Discord,Money,XP,last_message,Level) VALUES ('{user.id}','0','0','0','1')"
    cur.execute(query_add_user)
    mydb.commit()
    print(f"{user.id} added to DB")
    await ctx.send(f"User : {user} added to DataBase")

@slash.slash(guild_ids=guild_ids,description="Montre ton XP",options=[
    create_option(
        name="user",
        description="Voir le niveau d'un utilisateur",
        option_type=6,
        required=False,
        )
    ]
)
async def level(ctx : SlashContext,user=NULL):
    if user!=NULL:
        level=global_function.get_player_level(user.id)
        XP_player=global_function.get_player_xp(user.id)
        XP_needed = global_function.get_level_xp(level)-XP_player
        level_xp=global_function.get_level_xp(level)-global_function.get_level_xp(level-1)
        XP_progress = level_xp-XP_needed
        embed=discord.Embed(
            title=f'XP de {user}',
            colour = discord.Colour.red(),
        )
        embed.set_thumbnail(url=user.avatar_url)
    
    if user==NULL:
        level=global_function.get_player_level(ctx.author.id)
        XP_player=global_function.get_player_xp(ctx.author.id)
        XP_needed = global_function.get_level_xp(level)-XP_player
        level_xp=global_function.get_level_xp(level)-global_function.get_level_xp(level-1)
        XP_progress = level_xp-XP_needed
        embed=discord.Embed(
            title=f'XP de {ctx.author}',
            colour = discord.Colour.red(),
        )
        embed.set_thumbnail(url=ctx.author.avatar_url)

    embed.set_footer(text='Support : Tomish#3832')
    embed.set_author(name="Civiz Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")

    embed.add_field(name=f"Niveau : {level}",value=f"XP : {XP_progress}/{level_xp}", inline=True)
    embed.add_field(name="Rank : ",value='Soon...', inline=True)
    embed.add_field(name="Progression :",value=f"{global_function.progress_bar(global_function.get_pourcentage(20,XP_needed,level_xp),20)}   {100-global_function.get_pourcentage(100,XP_needed,level_xp)}%", inline=False)
    await ctx.send(embed=embed)

@slash.slash(name="add",description="Add something to someone", guild_ids=guild_ids, options=[
        create_option(
            name="element",
            description="Choisir l'élément à ajouter au joueur",
            option_type=3,
            required=True,
            choices=[
                create_choice(
                    name="XP",
                    value="XP",
                ),
                create_choice(
                    name="Argent",
                    value="Argent",
                ),
                create_choice(
                    name="Level",
                    value="Level",
                ),
            ]
        ),
        create_option(
            name="user",
            description="Choisir l'utilisateur à qui ajouter le montant",
            option_type=6,
            required=True
        ),
        create_option(
            name="montant",
            description="Choisir le montant à ajouter",
            option_type=4,
            required=True,
        )
    ]
)
async def add(ctx : SlashContext,element,user,montant):
    print(element)
    if element=="XP":
        cur=mydb.cursor()
        query_add_xp=f"update player set XP = (SELECT XP WHERE ID_Discord='{user.id}')+{montant} where ID_Discord = {user.id}"
        cur.execute(query_add_xp)
        mydb.commit()

        while global_function.get_player_level(user.id) > global_function.get_level_xp(global_function.get_player_level(user.id)):
            query_levelup= f"update player set level =(SELECT level WHERE ID_Discord='{user.id}')+1 where ID_Discord='{user.id}'"
            cur.execute(query_levelup)
            mydb.commit()
        await ctx.send(f"Ajout de {montant} XP à {user}, XP Total du joueur : {global_function.get_player_xp(user.id)} XP. Niveau mis à jour")

    if element=="Argent":
        cur=mydb.cursor()
        query_add_money=f"update player set argent ={global_function.get_player_money(user.id)+montant} where ID_Discord={user.id}"
        cur.execute(query_add_money)
        mydb.commit()

    if element=="Level":
        cur=mydb.cursor()
        query_add_level=f"update player set level = {global_function.get_player_level(user.id)+montant}, xp={global_function.get_level_xp(global_function.get_player_level(user.id)+montant-1)} where ID_Discord = {user.id}"
        await ctx.send(f"{user} is now level {global_function.get_player_level(user.id)+montant}")
        cur.execute(query_add_level)
        mydb.commit()

@slash.slash( name='money', options=[
    create_option(
        name='user',
        required=False,
        option_type=6,
        description="Choisir l'utilisateur à qui visualiser le port-feuille",
        )
    ],guild_ids=guild_ids
)
async def money(ctx : SlashContext,user= NULL):
    if user==NULL:
        embed=discord.Embed(
        title=f'Argent de {ctx.author}',
        colour = discord.Colour.green(),
        )
        embed.set_footer(text="/baltop pour voir le classement d'argent")
        embed.set_author(name="Civiz Trading Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name=f"Seuil du port-monnaie : ",value=f"{global_function.get_player_money(ctx.author.id)}", inline=True)
    else :
        embed=discord.Embed(
        title=f'Argent de {user}',
        colour = discord.Colour.green(),
        )
        embed.set_footer(text="/baltop pour voir le classement d'argent")
        embed.set_author(name="Civiz Trading Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name=f"Seuil du port-monnaie : ",value=f"{global_function.get_player_money(ctx.author.id)}", inline=True)
    await ctx.send(embed=embed)

@slash.slash(name="classement",description="Affiche le classement des gens les plus riches",guild_ids=guild_ids,options=[create_option(
    name="page",
    description="Aller à la page correspondante",
    option_type=4,
    required=False,
)])
async def classement(ctx : SlashContext,page=NULL):
    if page ==NULL :
        page = 1
    vector=global_function.get_classement()
    if page > (len(vector)//10+1):
        await ctx.send(f"La page entré n'existe pas, le nombre maximal de pages est de {len(vector)//10+1}.")
        return 0
    classement_text=""
    if page*10>len(vector):
        page_max=len(vector)-(10*(page-2))
    else :
        page_max=page*10
    for i in range(((10*page-10)),(page_max),1):
        classement_text=f"{classement_text} [{i+1}] - <@{vector[i][1]}> : {vector[i][0]} ₵\n"
    embed=discord.Embed(
    title=f'Classement argent :',
    colour = discord.Colour.green(),
    )
    file = discord.File("ranking.png")
    embed.set_footer(text=f"Page {page} sur {len(vector)//10+1}, une page peut-être précisé pour voir le classement en précision")
    embed.set_author(name="Civiz Trading Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")
    embed.set_thumbnail(url="attachment://ranking.png")
    embed.add_field(name=f"Classement : ",value=f"{classement_text}", inline=True)
    await ctx.send(file = file,embed=embed)


client.run(token)
