import discord
import aiohttp
import asyncio
import time
import random
import bson
import re, os, sys
import sqlite3
from discord.ext import commands

#BOT#PARAMS###################################################################################################
TOKEN = ''
userid = '695328763960885269'
version = '0.0.1'
myname = "Fishy.py"
invite = "https://discordapp.com/api/oauth2/authorize?client_id=695328763960885269&permissions=8&scope=bot"
client = discord.Client()

#CONFIG#######################################################################################################
defaultprefix = "!"
secondstoReact = 7

#DB#MANAGEMENT################################################################################################
if os.path.isfile('fishypy.db'):
    db_exists = True
    conn = sqlite3.connect('fishypy.db')
    c = conn.cursor()
else:
    conn = sqlite3.connect('fishypy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE fishyusers
             (userid text, totalcaught text, rodlevel text, userlevel text, trophyname text, trophylength text, guild text)''') #i make them all text so its easier
             # userid = the users id (int)
             # total caught = total number of fish caught (int)
             # rodlevel = the rod level (int)
             # userlevel = that users level (int)
             # trophyname = name of best fish caught (string)
             # trophylength = length of best fish caught (string)[ex: "4.56cm"]
             # guild = the guild the user belongs to (int)
    c.execute("INSERT INTO fishyusers VALUES ('267410788996743168','0','0','0','none','none','0')") # this is me
    c.execute('''CREATE TABLE fishyguilds
             (guildid text, guildtotal text, adminsid text, globalpos text)''')
             #guildid = the guilds id (int)
             #guildtotal = total number of fish caught ever in guild (int)
             #adminsid = the admins user id (int)
             #globalpos = the guilds global position out of the rest of the guilds (int)
    c.execute("INSERT INTO fishyguilds VALUES ('695330969527517294','0','267410788996743168','1')") # this is bot emporium server
conn.commit()
#c.execute('SELECT * FROM fishy')
bson_file = open('fishes.bson', 'rb')
b = bson.loads(bson_file.read())
print(b)

helpmsg = """```
React on message to fish, rods are auto-upgraded
Compete with others for best collection
#______COMMANDS______#
[!fish][to start fishing]
[!profile][player profile, rod level, collection]
[!top (rod,collection)][Leaderboards]
[!prefix][changing bot prefix for server(admins only)]
[!info][info and stats about bot]
[!invite][to invite bot to your discord server]
```"""

def grabusers():
    c.execute('SELECT * FROM fishyusers')
    data = c.fetchall()
    for i in data:
        print(i)
def addusers(authorid,guildid,authorname):
    c.execute('SELECT * FROM fishyusers')
    data = c.fetchall()
    for i in data:
        if authorid == i[0]:
            returnmsg = "```\nYou're already in the database.\n```"
        else:
            c.execute(f"INSERT INTO fishyusers VALUES ('{authorid}','0','0','0','none','none','{guildid}')")
            returnmsg = (f"```\nHey {authorname}, ive added you to the database.\n```")
    return(returnmsg)

@client.event
async def on_message(message):

    ts = time.gmtime()
    data = c.fetchall()
    conn.commit()

    guildid = message.guild.id #guild check
    authorid = message.author.id
    authorname = message.author.name

    if message.content.startswith('!debug'):
        grabusers()
        await message.channel.send("```\nCheck console!\n```")
        
    if message.content.startswith('!start'):
        c.execute('SELECT * FROM fishyusers')
        addusers(authorid,guildid,authorname) #todo: fix this mess
        msg = addusers()
        conn.commit()
        await message.channel.send(msg)

@client.event
async def on_ready():
    print('------------------------------------------------')
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------------------------------------------------')
    print(myname, version,"is connected and running")
    print('------------------------------------------------')

client.run(TOKEN)