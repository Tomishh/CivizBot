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

def get_pourcentage(n,a,b):
    value = ((n*a)/b)
    return int(value)

def progress_bar(n,a):
    full="█"
    empty="░"
    string=""
    for i in range(a-n):
        string=f"{string}{full}"
    for j in range(n):
        string=f"{string}{empty}"
    return string
