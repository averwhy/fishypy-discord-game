import discord
import aiohttp
import asyncio
import time
import random
import json
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
defaultprefix = "f:"
bot = commands.Bot(command_prefix=defaultprefix)
secondstoReact = 7

#DB#MANAGEMENT################################################################################################
if os.path.isfile('fishypy.db'):
    db_exists = True
    conn = sqlite3.connect('fishypy.db')
    c = conn.cursor()
    print("Database found.")

else:
    conn = sqlite3.connect('fishypy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE fishyusers
             (userid text, totalcaught text, rodlevel text, userlevel text, trophyname text, trophylength text, guild text, isadmin text)''') #i make them all text so its easier
             # userid = the users id (int)
             # total caught = total number of fish caught (int)
             # rodlevel = the rod level (int)
             # userlevel = that users level (int)
             # trophyname = name of best fish caught (str)
             # trophylength = length of best fish caught (str)[ex: "4.56cm"]
             # guild = the guild the user belongs to (int)
             # isadmin = if they are a fishy admin NOT SERVER ADMIN (bool)
    c.execute("INSERT INTO fishyusers VALUES ('267410788996743168','0','0','0','none','none','0','true')") # this is me
    c.execute('''CREATE TABLE fishyguilds
             (guildid text, guildtotal text, globalpos text, topuser text, guildtrophyname text, guildtrophylength text)''')
             #guildid = the guilds id (int)
             #guildtotal = total number of fish caught ever in guild (int)
             #globalpos = the guilds global position out of the rest of the guilds (int)
             #topuser = the guilds top user (int)
             #guildtrophyname = the guilds trophy fish, name (str)
             #guildtrophylength = the guilds trophy fish, length (str)
    c.execute("INSERT INTO fishyguilds VALUES ('695330969527517294','0','267410788996743168','1','none','none')") # this is bot emporium server
    print("Database not found. Necessary values were inserted.")
conn.commit()
#c.execute('SELECT * FROM fishy')
fishy_json = open("C:\\Users\\aver\\Documents\\GitHub\\fishy-discord-game\\fishy.json")
json_data = json.loads(fishy_json)

helpmsg = """```md
React on message to fish, rods are auto-upgraded
Compete with others for best collection
#______COMMANDS______#
[!fish][to start fishing] < WIP >
[!profile][player profile, rod level, trophy]
[!top (guilds,users)][Leaderboards] < WIP >
[!prefix][changing bot prefix for server(admins only)] < WIP >
[!info][info and stats about bot] < WIP >
[!invite][invite bot to your discord server] < WIP >
[!myguild][change the guild you belong to] < WIP >
[!help][show this message]
```"""

def grabusers():
    c.execute('SELECT * FROM fishyusers')
    data = c.fetchall()
    for i in data:
        print(i)


def addusers(authorid,guildid,authorname):
    c.execute('SELECT * FROM fishyusers')
    data = c.fetchall()
    authorid = int(authorid)
    founduser = False
    # idtofetch = c.execute(f"SELECT userid FROM fishyusers WHERE userid = {authorid}")
    # returnmsg = idtofetch
    for i in data:
        idtocheck = int(i[0])
        print(idtocheck,"and",authorid)
        if authorid == idtocheck:
            returnmsg = "`You're already in the database.`"
            founduser = True
            break

    else:    
        c.execute(f"INSERT INTO fishyusers VALUES ('{authorid}','0','0','0','none','none','{guildid}','false')")
        returnmsg = (f"`Hey {authorname}, ive added you to the database.`")
        conn.commit()

    return(returnmsg)

def getprofile(authorid,guildid,authorname):
    c.execute('SELECT * FROM fishyusers')
    data = c.fetchall()
    authorid = int(authorid)
    for i in data:
        idtocheck = int(i[0])
        print(idtocheck,"and",authorid)
        if authorid == idtocheck:
            list_to_return = []
            list_to_return.append(i[0])
            list_to_return.append(i[1])
            list_to_return.append(i[2])
            list_to_return.append(i[3])
            list_to_return.append(i[4])
            list_to_return.append(i[5])
            list_to_return.append(i[6])
            print(list_to_return)
    else:
        returnmsg = "`I was unable to retrieve your profile. Have you done !start yet?"
        
    return(list_to_return)

@client.event
async def on_message(message):

    ts = time.gmtime()
    data = c.fetchall()
    conn.commit()

    if message.content.startswith(f'{defaultprefix}debug'):
        if message.author.id == 267410788996743168:
            grabusers()
            await message.channel.send(content=(f"`Check console`"))
        else:
            await message.channel.send(content="`Insufficent permission`")
        
    if message.content.startswith(f'{defaultprefix}start'):
        authorid = message.author.id
        authorname = message.author.name
        guildid = message.guild.id #guild check
        msgtoedit = await message.channel.send("`Please wait...`")
        c.execute('SELECT * FROM fishyusers')
        returnedmsg = addusers(authorid,guildid,authorname)
        await asyncio.sleep(1)
        await msgtoedit.edit(content=(returnedmsg))
        conn.commit()
    
    if message.content.startswith(f'{defaultprefix}profile'):
        authorid = message.author.id
        authorname = message.author.name
        guildid = message.guild.id #guild check
        guildname = message.guild.name
        returnedlist = getprofile(authorid,guildid,authorname)
        
        embed = discord.Embed(title=f"**User Profile**", description="", colour=discord.Colour(0x7a19fd))
        embed.set_author(name=f"{authorname}")
        embed.set_footer(text=f"Fishy.py - {version}",icon_url=(message.author.avatar_url))
        embed.add_field(name="Total fish caught", value=f"{returnedlist[1]}", inline=False)
        embed.add_field(name="Rod level", value=f"{returnedlist[2]}", inline=False)
        embed.add_field(name="User level", value=f"{returnedlist[3]}", inline=False)
        embed.add_field(name="Trophy", value=f"{returnedlist[4]}", inline=False)
        await message.channel.send(embed=embed)
    
    if message.content.startswith('!help'):
        await message.channel.send(helpmsg)

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