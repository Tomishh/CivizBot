import mysql.connector
import csv

list=[]

def get_level_xp(level):
    return (5*(level*level)+(50*level)+100)

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


def get_classement():
    cur=mydb.cursor()
    query_money = f"SELECT money,ID_discord from player ORDER BY money DESC"
    cur.execute(query_money)
    player_classement=cur.fetchall()
    return player_classement

