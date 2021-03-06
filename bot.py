from asyncio.windows_events import NULL
from configparser import DEFAULTSECT
from inspect import getfullargspec
from os import name
import os
import re
import discord
from discord import embeds
from discord.ext import commands
from discord.ext.commands.core import check
from discord.flags import Intents
from discord.player import CREATE_NO_WINDOW
from discord_slash import SlashCommand, SlashCommandOptionType , SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option,wait_for_component

from discord_slash.model import ButtonStyle
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

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def get_player_level(user):
    cur=mydb.cursor()
    query_level = f"SELECT level from player WHERE ID_Discord='{user}'"
    cur.execute(query_level)
    player_level=cur.fetchall()
    return player_level[0][0]

def get_player_xp(user):
    cur=mydb.cursor()
    query_xp = f"SELECT XP from player WHERE ID_Discord='{user}'"
    cur.execute(query_xp)
    player_xp=cur.fetchall()
    return player_xp[0][0]

def get_player_last_message(user):
    cur=mydb.cursor()
    query_timestamp=f"select last_message from player where ID_Discord = {user}"
    cur.execute(query_timestamp)
    last_message=cur.fetchall()
    return last_message[0][0]

def get_player_money(user):
    cur=mydb.cursor()
    query_timestamp=f"select money from player where ID_Discord = {user}"
    cur.execute(query_timestamp)
    money=cur.fetchall()
    return money[0][0]

def get_classement():
    cur=mydb.cursor()
    query_classement = f"SELECT money,ID_discord from player ORDER BY money DESC"
    cur.execute(query_classement)
    player_classement=cur.fetchall()
    return player_classement

def get_level_xp(level):
    return (5*(level*level)+(50*level)+100)

def get_player_new_level(player):
    cur=mydb.cursor()
    query_reset_level=f"update player set level=1 where ID_Discord={player}"
    cur.execute(query_reset_level)
    mydb.commit()
    while get_player_xp(player) > get_level_xp(get_player_level(player)):
        query_new_level=f"update player set level={get_player_level(player)+1} where ID_Discord={player}"
        cur.execute(query_new_level)
        mydb.commit()
        print("level added")

def get_pourcentage(n,a,b):
    value = ((n*a)/b)
    return int(value)

def progress_bar(n,a):
    full="???"
    empty="???"
    string=""
    for i in range(a-n):
        string=f"{string}{full}"
    for j in range(n):
        string=f"{string}{empty}"
    return string

def is_hex_color(input_string):
    HEX_COLOR_REGEX = r'^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    regexp = re.compile(HEX_COLOR_REGEX)
    if regexp.search(input_string):
        return True
    return False

def create_folder_options(path_choice):
    directory_list = []
    for root, dirs, files in os.walk(f"{path_choice}", topdown=False):
        for name in dirs:
            directory_list.append(os.path.join(root, name))

    new_directory_list= []
    for i in range(len(directory_list)):
        new_directory_list.append(directory_list[i].replace(f"{path_choice}","")),
    return_list= []
    for i in range(len(new_directory_list)):
        return_list.append(create_select_option(f"{new_directory_list[i]}", value=f"{new_directory_list[i]}"))
        print(f"droplist {new_directory_list[i]}cr??e")
    return return_list

def create_commands_choice(path_choice):
    directory_list = []
    for root, dirs, files in os.walk(f"{path_choice}", topdown=False):
        for name in dirs:
            directory_list.append(os.path.join(root, name))

    new_directory_list= []
    for i in range(len(directory_list)):
        new_directory_list.append(directory_list[i].replace(f"{path_choice}","")),
    return_list= []
    for i in range(len(new_directory_list)):
        return_list.append(create_choice(name=f"{new_directory_list[i]}",value=f"{new_directory_list[i]}"))
        print(f"choice {new_directory_list[i]} cr??e")
    return return_list

def post_embed(ctx, project):
    if os.path.isfile(f"embed/{project}/{project}_title.txt")==False:
        ctx.send(f"Aucun titre pour l'embed")
        return 0
    if os.path.isfile(f"embed/{project}/{project}_description.txt")==False:
        with open(f"embed/{project}/{project}_title.txt", 'r') as file:
            data = file.read()
        embed=discord.Embed(
        title=data,
        )

    if os.path.isfile(f"embed/{project}/{project}_description.txt")==True:
        with open(f"embed/{project}/{project}_title.txt", 'r') as file:
            data_title = file.read()
        with open(f"embed/{project}/{project}_description.txt", 'r') as file:
            data = file.readlines()
            data_description=""
            for line in data:
                data_description =data_description+line
        embed=discord.Embed(
        title=data_title,
        description=data_description,
        )
    for i in range(1,25):
        if os.path.isfile(f"embed/{project}/{project}_section_message_{i}.txt")==True and os.path.isfile(f"embed/{project}/{project}_section_titre_{i}.txt")==True:
            with open(f"embed/{project}/{project}_section_titre_{i}.txt", 'r') as file:
                data_section_title = file.read()
            with open(f"embed/{project}/{project}_section_message_{i}.txt", 'r') as file:
                data = file.readlines()
                data_section_description=""
                for line in data:
                    data_section_description =data_section_description+line
            embed=embed.add_field(name=data_section_title,value=data_section_description)
    return embed

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
        last_message_delay=get_player_last_message(message.author.id)+20
        actual_time=int(time.time())
        if last_message_delay<actual_time: #   AJOUT DE L'XP ET DE L'ARGENT
            cur=mydb.cursor()
            query_addxp=f"update player set XP ={get_player_xp(message.author.id)+3},money='{get_player_money(message.author.id)+5}', last_message='{actual_time}' where ID_Discord='{message.author.id}'"
            cur.execute(query_addxp)
            print(f"{message.author} XP added and last_message updated")
            mydb.commit()
            needed_xp = (5*(get_player_level(message.author.id)**2)+(50*get_player_level(message.author.id))+100)
            if get_player_xp(message.author.id) > needed_xp:
                await message.channel.send(f"<@{message.author.id}> a Level-up ! Tu es pass?? niveau {get_player_level(message.author.id)+1}")
                query_levelup= f"update player set level =(SELECT level WHERE ID_Discord='{message.author.id}')+1 where ID_Discord='{message.author.id}'"
                cur.execute(query_levelup)
                mydb.commit()
                
                print(f"{message.author} level up !")
        else:
            print(f"Message sended too early by {message.author} to add XP")

@slash.slash(guild_ids=guild_ids,description='??a fait prout')
async def hi(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send("Bonjour mon reuf 3")

@slash.slash(guild_ids=guild_ids,description="Show latency")
async def ping(ctx : SlashContext, guild_ids=guild_ids):
    await ctx.send(f"Bot speed : {round(client.latency *1000)}ms")

@slash.slash(guild_ids=guild_ids,description="Pong comme on dit")
async def test2(ctx : SlashContext):
    message= await ctx.channel.fetch_message(ctx.channel.last_message_id)
    await ctx.send(message.content)
    await ctx.send(f"Wsh wsh wsh <@{ctx.author_id}>,{ctx.channel.last_message_id}")


@slash.slash(guild_ids=guild_ids,name="useraddDB", description="ajoute utilisateur a la bdd", options=[{
    "name": "user",
    "description": "S??lectionne l'utilisateur ?? ajouter ?? la BDD",
    "type": 6,
    "required": "true"
    },])

async def useraddDB(ctx : SlashContext,user, guild_ids=guild_ids):
    cur=mydb.cursor()
    query_add_user=f"insert into player (ID_Discord,Money,XP,last_message,Level) VALUES ('{user.id}','0','0','0','1')"
    cur.execute(query_add_user)
    mydb.commit()
    print(f"{user.id} added to DB")
    await ctx.send(f"User : {user.name} added to DataBase")

@slash.slash(guild_ids=guild_ids,description="Montre ton XP",options=[
    create_option(
        name="user",
        description="Voir le niveau d'un utilisateur",
        option_type=6,
        required=False,
        )])

async def level(ctx : SlashContext,user=NULL):
    if user!=NULL:
        level=get_player_level(user.id)
        XP_player=get_player_xp(user.id)
        XP_needed = get_level_xp(level)-XP_player
        level_xp=get_level_xp(level)-get_level_xp(level-1)
        XP_progress = level_xp-XP_needed
        embed=discord.Embed(
            title=f'XP de {user.name}',
            colour = discord.Colour.red(),
        )
        embed.set_thumbnail(url=user.avatar_url)
    
    if user==NULL:
        level=get_player_level(ctx.author.id)
        XP_player=get_player_xp(ctx.author.id)
        XP_needed = get_level_xp(level)-XP_player
        level_xp=get_level_xp(level)-get_level_xp(level-1)
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
    embed.add_field(name="Progression :",value=f"{progress_bar(get_pourcentage(20,XP_needed,level_xp),20)}   {100-get_pourcentage(100,XP_needed,level_xp)}%", inline=False)
    await ctx.send(embed=embed)

@slash.slash(name="add",description="Add something to someone", guild_ids=guild_ids, options=[
        create_option(
            name="element",
            description="Choisir l'??l??ment ?? ajouter au joueur",
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
            description="Choisir l'utilisateur ?? qui ajouter le montant",
            option_type=6,
            required=True
        ),
        create_option(
            name="montant",
            description="Choisir le montant ?? ajouter",
            option_type=4,
            required=True,
        )])
async def add(ctx : SlashContext,element,user,montant):
    print(element)
    if element=="XP":
        cur=mydb.cursor()
        query_add_xp=f"update player set XP = (SELECT XP WHERE ID_Discord='{user.id}')+{montant} where ID_Discord = {user.id}"
        cur.execute(query_add_xp)
        mydb.commit()
        get_player_new_level(user.id)
        await ctx.send(f"Ajout de {montant} XP ?? {user.name}, XP Total du joueur : {get_player_xp(user.id)} XP. Niveau mis ?? jour")

    if element=="Argent":
        cur=mydb.cursor()
        query_add_money=f"update player set Money ={get_player_money(user.id)+montant} where ID_Discord={user.id}"
        cur.execute(query_add_money)
        mydb.commit()
        await ctx.send(f"L'argent de {user.name} vient d'??tre mis ?? jour, {user.name} poss??de d??sormais {get_player_money(user.id)}")

    if element=="Level":
        cur=mydb.cursor()
        print(f"futur xp : {get_level_xp(get_player_level(user.id)+montant-1)}")
        print(f"level futur : {get_player_level(user.id)+montant}")
        query_add_level=f"update player set level = {get_player_level(user.id)+montant}, xp={get_level_xp(get_player_level(user.id)+montant-1)} where ID_Discord = {user.id}"
        await ctx.send(f"{user.name} is now level {get_player_level(user.id)+montant}")
        cur.execute(query_add_level)
        mydb.commit()

@slash.slash(name="remove",description="Enleve ?? un utilisateur un  ??l??ment", guild_ids=guild_ids, options=[
    create_option(
        name="element",
        description="Element ?? enlever ?? l'utilsateur",
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
            )
        ]
    ),
    create_option(
        name="user",
        description="Utilisateur ?? qui le retrait va s'appliquer",
        option_type=6,
        required=True
    ),
    create_option(
        name="montant",
        description="Montant du retrait",
        required=True,
        option_type=4,
    )])
async def remove(ctx : SlashContext,user,montant,element):
    cur=mydb.cursor()
    if element=="XP":
        if get_player_xp(user.id) < montant:
            query_xp=f"update player set XP='100' where ID_Discord={user.id}"
        else :
            query_xp=f"update player set XP={get_level_xp(get_player_level(user.id))-montant} where ID_Discord={user.id}"
        cur.execute(query_xp)
        mydb.commit()
        if get_player_xp(user.id) < 100:
            query_new_xp=f"update player set xp=100 where ID_discord = {user.id}"
        get_player_new_level(user.id)
        await ctx.send(f"L'XP de {user.name} vient d'??tre mis ?? jour, son XP est d??sormais ??gal ?? : {get_player_xp(user.id)}")
    if element=="Argent": 
        if get_player_money(user.id) < montant:
            query_argent=f"update player set Money='0' where ID_Discord={user.id}"
        else : 
            query_argent=f"update player set Money='{get_player_money(user.id)-montant}' where ID_Discord={user.id}"
        cur.execute(query_argent)
        mydb.commit()
        await ctx.send(f"L'argent de {user.name} vient d'??tre mis ?? jour, {user.name} poss??de maintenant {get_player_money(user.id)}???")
    if element=="Level":
        if get_player_level(user.id) < montant:
            query_level=f"update player set level=0 where ID_Discord = {user.id}"
        else :
            query_level=f"update player set level='{get_player_level(user.id)-montant}' where ID_Discord = {user.id}"
        cur.execute(query_level)
        query_new_xp=f"update player set xp={get_level_xp(get_player_level(user.id)-1)} where ID_Discord = {user.id}"
        cur.execute(query_new_xp)
        mydb.commit()
        await ctx.send(f"Le niveau de {user.name} vient d'??tre mis ?? jour, {user.name} est maintenant niveau {get_player_level(user.id)}")
        
@slash.slash(name="set",description="Element ?? changer", guild_ids=guild_ids, options=[
    create_option(
        name="element",
        description="Element ?? changer ?? l'utilsateur",
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
            )
        ]
    ),
    create_option(
        name="user",
        description="Utilisateur ?? qui le changement va s'appliquer",
        option_type=6,
        required=True
    ),
    create_option(
        name="montant",
        description="Nouveau montant de l'element",
        required=True,
        option_type=4,
    )])
async def set(ctx : SlashContext,user,element,montant):
    cur=mydb.cursor()
    if element=="XP":
        query_xp=f"update player set XP={montant} where ID_Discord={user.id}"
        cur.execute(query_xp)
        mydb.commit() 
        get_player_new_level(user.id)
        await ctx.send(f"XP et niveaux mis ?? jour pour {user.name}")
    if element=="Argent":
        query_argent=f"update player set money={montant} where ID_discord={user.id}"
        cur.execute(query_argent)
        mydb.commit
        await ctx.send(f"L'argent de {user.name} vient d'??tre mise ?? jour, {user.name} poss??de d??sormait {get_player_money(user.id)}")
    if element=="Level":
        query_level=f"update player set level={montant},xp={get_level_xp(montant-1)} where ID_Discord={user.id}"
        cur.execute(query_level)
        mydb.commit()
        await ctx.send(f"Le niveau et l'XP ont ??t?? mis ?? jour pour {user.name}") 

@slash.slash(name="reset",description="R??initialise le niveau du joueur",guild_ids=guild_ids,options=[
    create_option(
        name="user",
        description="Utilisateur ?? qui la r??initialisation va s'appliquer",
        option_type=6,
        required=True,
    )])

async def reset(ctx : SlashContext,user):
    cur=mydb.cursor()
    query_reset=f"update player set XP=100,money=0,Level=1 where ID_Discord={user.id}"
    cur.execute(query_reset)
    mydb.commit()
    await ctx.send(f"L'XP, le niveau ainsi que l'argent de {user.name} a ??t?? r??initialis??")

@slash.slash( name='money', options=[
    create_option(
        name='user',
        required=False,
        option_type=6,
        description="Choisir l'utilisateur ?? qui visualiser le port-feuille",
        )
    ],guild_ids=guild_ids)
async def money(ctx : SlashContext,user= NULL):
    if user==NULL:
        embed=discord.Embed(
        title=f'Argent de {ctx.author}',
        colour = discord.Colour.green(),
        )
        embed.set_footer(text="/baltop pour voir le classement d'argent")
        embed.set_author(name="Civiz Trading Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name=f"Seuil du port-monnaie : ",value=f"{get_player_money(ctx.author.id)}", inline=True)
    else :
        embed=discord.Embed(
        title=f'Argent de {user.name}',
        colour = discord.Colour.green(),
        )
        embed.set_footer(text="/baltop pour voir le classement d'argent")
        embed.set_author(name="Civiz Trading Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name=f"Seuil du port-monnaie : ",value=f"{get_player_money(ctx.author.id)}", inline=True)
    await ctx.send(embed=embed)

@slash.slash(name="classement",description="Affiche le classement des gens les plus riches",guild_ids=guild_ids,options=[create_option(
    name="page",
    description="Aller ?? la page correspondante",
    option_type=4,
    required=False
    )])
async def classement(ctx : SlashContext,page=NULL):
    if page ==NULL :
        page = 1
    vector=get_classement()
    if page > (len(vector)//10+1):
        await ctx.send(f"La page entr?? n'existe pas, le nombre maximal de pages est de {len(vector)//10+1}.")
        return 0
    classement_text=""
    if page*10>len(vector):
        page_max=len(vector)-(10*(page-2))
    else :
        page_max=page*10
    for i in range(((10*page-10)),(page_max),1):
        classement_text=f"{classement_text} [{i+1}] - <@{vector[i][1]}> : {vector[i][0]} ???\n"
    embed=discord.Embed(
    title=f'Classement argent :',
    colour = discord.Colour.green(),
    )
    file = discord.File("ranking.png")
    embed.set_footer(text=f"Page {page} sur {len(vector)//10+1}, une page peut-??tre pr??cis?? pour voir le classement en pr??cision")
    embed.set_author(name="Civiz Trading Bot",icon_url="https://cdn.discordapp.com/avatars/854067274892967937/31c3d848d1796a79083c1acf95475ee0.webp?size=128")
    embed.set_thumbnail(url="attachment://ranking.png")
    embed.add_field(name=f"Classement : ",value=f"{classement_text}", inline=True)
    await ctx.send(file = file,embed=embed)

@slash.subcommand(base="embed",name="create",description="ajoute un nom de projet",guild_ids=guild_ids,options=[
    create_option(
        name="project",
        description="Nom du projet",
        required=True,
        option_type=3
    )])
async def create(ctx : SlashContext, project):
    try:
        os.makedirs(f"embed/{project}")
    except:
        await ctx.send(f"Le projet avec le nom '{project}' existe d??j??.")
    with open(f"embed/{project}//{project}_created.txt","w") as f:
        f.write("created.")
    f.close()

    await ctx.send("done.")


@slash.subcommand(base="embed",name="title",description="titre",guild_ids=guild_ids,options=[
    create_option(
        name="project",
        description="Saisir le nom du projet",
        option_type=3,
        required=True,
    ),
    create_option(
        name="titre",
        description="Saisir le titre de l'embed ?? afficher",
        option_type=3,
        required=True,
    )])
async def title(ctx : SlashContext,titre,project):
    if os.path.isfile(f"embed/{project}/{project}_created.txt")==False:
        await ctx.send(f"Le projet '{project}' n'existe pas ")
        return 0
    with open(f"embed/{project}/{project}_title.txt","w") as f:
        f.write(titre)
    f.close()
    await ctx.send(embed=post_embed(ctx,project))

@slash.subcommand(base="embed",name="description",description="Ajoute votre pr??c??dent message en tant que description de l'embed",guild_ids=guild_ids,options=[
    create_option(
        name="project",
        description="Saisir le nom du projet",
        option_type=3,
        required=True,
    )])
async def description(ctx : SlashContext,project):
    if os.path.isfile(f"embed/{project}/{project}_created.txt")==False:
        await ctx.send(f"Le projet '{project}' n'existe pas ")
        return 0
    message= await ctx.channel.fetch_message(ctx.channel.last_message_id)
    with open(f"embed/{project}/{project}_description.txt","w") as f:
        f.write(message.content)
    f.close()
    await ctx.send(embed=post_embed(ctx,project))

@slash.subcommand(base="embed",name="section",description="Ajoute votre pr??c??dent message en tant que section dans l'embed",guild_ids=guild_ids,options=[
    create_option(
        name="project",
        description="Nom du projet",
        required=True,
        option_type=3
    ),
    create_option(
        name="numero",
        description="Numero de la section",
        required=True,
        option_type=4,
    ),
    create_option(
        name="titre",
        description="Titre de la section",
        required=True,
        option_type=3,
    )])
async def section(ctx : SlashContext,project,numero,titre):
    if os.path.isfile(f"embed/{project}/{project}_created.txt")==False:
        await ctx.send(f"Le projet '{project}' n'existe pas ")
        return 0
    message= await ctx.channel.fetch_message(ctx.channel.last_message_id)
    with open(f"embed/{project}/{project}_section_message_{numero}.txt","w") as f:
        f.write(message.content)
    f.close()
    with open(f"embed/{project}/{project}_section_titre_{numero}.txt","w") as f:
        f.write(titre)
    f.close()
    await ctx.send(f"La section numero {numero} du projet '{project}' a ??t?? cr????e :",embed=post_embed(ctx,project))

@slash.subcommand(base="embed",name="post",description="Publie l'embed",guild_ids=guild_ids,options=[
    create_option(
        name="project",
        description="Nom du projet",
        required=True,
        option_type=3
    ),
    create_option(
        name="channel",
        description="Choisir le canal textuel dans lequel l'embed doit-??tre envoy??",
        required=True,
        option_type=7,
    )])
async def post(ctx : SlashContext, project,channel):
    await channel.send(embed=post_embed(ctx, project))
    await ctx.send(f"Embed envoy?? dans <#{channel.id}>")

@slash.slash(name="bouton",description="test bouton",guild_ids=guild_ids)
async def bouton(ctx:SlashContext):

    await ctx.send(".",components=[create_actionrow(
        create_select(options=[
            create_select_option("Vert",value="#77B058",emoji='????'),
            create_select_option("Bleu",value="#53A9E9",emoji='????'),
            create_select_option("Violet",value="#AA8ED6",emoji='????'),
            create_select_option("Marron",value="#C1694F",emoji='????'),
            create_select_option("Rouge",value="#DB2E43",emoji='????'),
            create_select_option("Orance",value="#F4900C",emoji='????'),
            create_select_option("Jaune",value="#FDCB58",emoji='????'),
            create_select_option("Noir",value="#31373D",emoji='???'),
            create_select_option("Blanc",value="#E5E6E7",emoji='???'),
        ],
        placeholder="Choisi un projet",
        min_values=1,
        max_values=1))])
   

client.run(token)
1
