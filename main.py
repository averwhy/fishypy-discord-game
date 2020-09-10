import discord
import aiohttp
import asyncio
import time
import random, math
import json
import re, os, sys
import sqlite3
from discord.ext import commands
#CONFIG#######################################################################################################
description = '''Fishy.py is an fork of Deda#9999's original Fishy bot. Fishy.py is being rewritten in discord.py API. To see commands use ]help. Full description on the fishy.py discord server: discord.gg/HSqevex'''
defaultprefix = "]"
secondstoReact = 7
ownersID = 267410788996743168
fishCaughtInSession = 0
xpGainedinsession = 0
reviewChannel_id = 735206051703423036

#BOT#PARAMS###################################################################################################
TOKEN = ''
userid = '695328763960885269'
version = '0.8'
myname = "Fishy.py"
invite = "https://discordapp.com/api/oauth2/authorize?bot_id=695328763960885269&permissions=8&scope=bot"
bot = commands.Bot(command_prefix=defaultprefix,description=description)
#bot = discord.bot()
bot.remove_command('help')
time_started = time.localtime()
time.strftime("%Y-%m-%d %H:%M:%S",time_started)

#DB#MANAGEMENT################################################################################################
if os.path.isfile('fishypy.db'):
    db_exists = True
    conn = sqlite3.connect('fishypy.db')
    c = conn.cursor()
    #print("Database found.")

else:
    conn = sqlite3.connect('fishypy.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE fishyusers
             (userid text, totalcaught text, Level text, rank text, trophyoid text, guild text, hexcolor text, reviewmsgid text)''') #i make them all text so its easier
             # userid = the users id (int)
             # totalcaught = total number of fish caught (int)
             # Level = the Level (int)
             # trophyname = name of best fish caught (str)
             # trophylength = length of best fish caught (str)[ex: "4.56cm"]
             # guild = the guild id the user belongs to (int)
             # hexcolor = the color that appears on their profile embed (str)
             # reviewmsgid = the id of the review message the user submitted
    c.execute("INSERT INTO fishyusers VALUES ('267410788996743168','0','0.00','0','none','0','005dff','0')") # this is me

    c.execute('''CREATE TABLE fishyguilds
             (guildid text, guildtotal text, globalpos text, topuser text, guildtrophyoid text)''')
             #guildid = the guilds id (int)
             #guildtotal = total number of fish caught ever in guild (int)
             #globalpos = the guilds global position out of the rest of the guilds (int)
             #topuser = the guilds top user (int)
             #guildtrophyname = the guilds trophy fish, name (str)
             #guildtrophylength = the guilds trophy fish, length (str)
    c.execute("INSERT INTO fishyguilds VALUES ('695330969527517294','0','0','none','none')") # this is bot emporium server
    #print("Database not found. Necessary values were inserted.")
    conn.commit()

try: 
    c.execute('SELECT * FROM fishes')
except:
    print("#################################################")
    print("!!!FATAL ERROR !!!")
    print("Fishes table is not found!!! This is required for the bot!")
    print("#################################################")
    TOKEN = None # so bot cant start
    #print("Token variable was set to None, as the bot cannot start without the fishes database.")
conn.commit()
#BOT#CODE#####################################################################################################

helpmsg = f"""```md
React on message to fish, rods are auto-upgraded
Compete with others for best collection
#______COMMANDS______#
<default prefix="{defaultprefix}">
[fish][to start fishing]
[profile][player profile, Level, trophy, total caught]
[top (guilds,users)][Leaderboards] < WIP >
[info][info and stats about bot]
[invite][invite bot to your discord server] < WIP >
[myguild][change the guild you belong to] < WIP >
[profilecolor][change the embed color of your profile - TEMPORARILY DISABLED]
[support][join the fishy.py discord server]
[help][show this message]
```"""

def usercheck(authorid):
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    #print(data)
    if data is None:
        return False
    else:
        return True

def fish_success_update(authorid,guildid,rarity):
    global fishCaughtInSession
    global xpGainedinsession

    updatevalue = None
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    data = list(data)
    #level updates
    theirlevel = data[2]
    rarity = float(rarity)
    theirlevel = float(theirlevel)
    xptoadd = rarity / 100.0
    updatevalue = theirlevel + xptoadd
    str(updatevalue)
    c.execute(f"Update fishyusers set Level = {updatevalue} where userid = {authorid}")

    theirlevel = divmod(theirlevel,1)
    levelonly = theirlevel[0]
    newlevel = divmod(updatevalue,1)
    newlevelint = newlevel[0]
    if int(newlevelint) > int(levelonly):
        return True

    xptoadd = int(xptoadd)
    xpGainedinsession += xptoadd
    updatevalue = None

    updatevalue = int(data[1])
    updatevalue += 1
    str(updatevalue)
    c.execute(f"Update fishyusers set totalcaught = {updatevalue} where userid = {authorid}")

    #then the guilds
    c.execute(f'SELECT * FROM fishyguilds WHERE guildid = {guildid}')
    data = c.fetchone()
    print(data)
    data = list(data)
    updatevalue = int(data[1])
    updatevalue += 1
    str(updatevalue)
    c.execute(f"Update fishyguilds set guildtotal = {updatevalue} where guildid = {guildid}")
    conn.commit()
    fishCaughtInSession += 1

def rodmath(authorid):
    # what i plan for this so far is:
    # 1. the integer is their Level.
    # 2. the decimal part of this is their xp. this has a direct effect the progress bar
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    rodlvl = data[2]
def rodUpgradebar(rodlvl):
    return f"{'#' * (decimal := round(rodlvl % 1 * 40))}{'_' * (40 - decimal)}"
    returned_upgradeBar = rodUpgradebar(rodlvl)
    #print(returned_upgradeBar)
    
def deluser(authorid,idtoremove):
    ##print(authorid,"and",ownersID)
    if int(authorid) == int(ownersID):
        try:
            c.execute(f"DELETE FROM fishyusers WHERE userid = {idtoremove}")
            theirusername = bot.get_user(idtoremove)
            return f"`The user, {theirusername}, was removed from the database.`"
        except:
            return "`Something went wrong. That user might not be in the database, or there was another error.`"
    else:
        return "`ERROR: Missing permissions.`"

def addusers(authorid,guildid,guildname,authorname):
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    if data is not None:
        return (f"`You're already in the database, {authorname}`")
    else:
        c.execute(f"INSERT INTO fishyusers VALUES ('{authorid}','0','0.00','0','none','{guildid}','005dff','0')")
        returnmsg = (f"`Hey {authorname}, ive added you to the database.`")
        conn.commit()
    c.execute(f"SELECT * FROM fishyguilds WHERE guildid = {guildid}")
    data = c.fetchone()
    if data is None:
        print("the guild doesnt exist, so i shall add to database aswell")
        c.execute(f"INSERT INTO fishyguilds VALUES ('{guildid}','0','0','none','none')")
        conn.commit()
    return returnmsg

def getprofile(authorid,guildid,authorname):
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    authorid = int(authorid)
    ##print(data)
    if data is not None:
        return data
    else:
        return False #because they dont exist

def levelupcheck(authorid,lastxp):
    #ONLY SHOULD BE USED IF USERCHECK IS TRUE
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    authorid = int(authorid)

def fishing(authorid,guildid,authorname):
    c.execute('SELECT * FROM fishes ORDER BY RANDOM() LIMIT 1;')
    data = c.fetchone()
    print(data)
    data = list(data)
    return data

@bot.event
async def on_command_error(ctx, error):
    
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.message.add_reaction("\U00002753") # red question mark
        checkuser = usercheck(ctx.message.author.id)
        if checkuser == False:
            await ctx.message.author.send(f"Hey there! I couldnt recognize that command. Maybe try using `{defaultprefix}help` instead? **Note: this message is only sent to users absent in the database.*")
    else:
        errorchannel = await bot.fetch_channel(741848294581600337)
        embed = discord.Embed(title="An error has occured!", description=f"{error}", colour=discord.Colour(0xfcd703))
        embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
        await asyncio.sleep(0.1)
        await ctx.send(embed=embed)
        await errorchannel.send(embed=embed)

@bot.command()
async def top(ctx,type):
    await ctx.send(f"`Sorry {ctx.author.name}, this command isnt avaliable yet.`")

@bot.command()
async def fish(ctx):
    channel = ctx.message.channel
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    checkuser = usercheck(authorid)
    if checkuser == False:
        await ctx.send("`I was unable to retrieve your profile. Have you done ]start yet?`")
    else:
        embed = discord.Embed(title=f"**React to fish!**", description="", colour=discord.Colour(0x000000))
        embed.set_footer(text=f"Fishy.py - {version} | Requested by {authorname}",icon_url=(bot.user.avatar_url))
        msgtoedit = await ctx.send(embed=embed)
        await msgtoedit.add_reaction(emoji="\U0001f41f") # fish emoji
        await msgtoedit.add_reaction(emoji="\U0001f419") # octopus
        await msgtoedit.add_reaction(emoji="\U0001f420") # tropical fish
        reactionList = ["\U0001f41f","\U0001f419","\U0001f420"]
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactionList
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            returnedlist = fishing(authorid,guildid,authorname)
            rarity = returnedlist[2]
            lvl_up_bool = fish_success_update(authorid,guildid,rarity)
            if lvl_up_bool is not None:
                await ctx.send(f"`Hey `{ctx.author.mention}`, you leveled up!! Congrats!`")
            ##print(returnedlist)
            xp = float(returnedlist[2])
            xp2 = xp/100
            embed = discord.Embed(title=f"**{returnedlist[5]}**", description="", colour=discord.Colour(0x7a19fd))
            embed.set_footer(text=f"Fishy.py - {version} | Requested by {authorname}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="XP Gained", value=f"{xp2}", inline=False)
            raritycalc = float(returnedlist[2])
            raritycalc2 = None
            if raritycalc > 0.8:
                raritycalc2 = "Legendary"
            if raritycalc > 0.6:
                raritycalc2 = "Rare"
            if raritycalc > 0.55:
                raritycalc2 = "Uncommon"
            if raritycalc > 0:
                raritycalc2 = "Common"
            embed.add_field(name="Rarity",value=f"{raritycalc2} ({returnedlist[2]})",inline=False)
            embed.add_field(name="Length", value=f"{returnedlist[4]}cm", inline=False)
            embed.add_field(name="# in database", value=f"{returnedlist[3]}/16205 fishes", inline=False)
            embed.set_image(url=returnedlist[1])
            await msgtoedit.clear_reactions()
            await asyncio.sleep(0.1)
            await msgtoedit.edit(embed=embed)
            
    conn.commit()

@bot.command()
async def support(ctx):
    await ctx.send("`The support server's invite link is` http://discord.gg/HSqevex")

@bot.command()
async def removeuser(ctx,idtoremove):
    authorid = ctx.message.author.id
    ylist = ["Y","yes","Yes","y","yEs"]
    idtoremove = int(idtoremove)
    userfromarg = bot.get_user(idtoremove)
    await ctx.send(f"`Are you sure you want to remove {userfromarg}({idtoremove}) from the database? [Respond with Y]` ```diff\n- THIS DATA IS NOT RECOVERABLE. YOU WILL LOSE IT PERMANENTLY! -\n```")
        
    def check(m):
        return m.content in ylist and m.channel == ctx.message.channel
    msg = await bot.wait_for('message', timeout=secondstoReact,check=check)
    returnedmsg = deluser(authorid,idtoremove)
    await ctx.send(returnedmsg)
    conn.commit()

@bot.command()
async def setvalue(ctx, idtomodify, valuetomodify, newvalue):
    if ctx.message.author.id == 267410788996743168:
        authorid = ctx.message.author.id
        idtomodify = int(idtomodify)
        try:
            c.execute(f'SELECT * FROM fishyusers WHERE userid = {idtomodify}')
            beforedata = c.fetchone()
            c.execute(f"Update fishyusers set {valuetomodify} = {newvalue} where userid = {idtomodify}")
            c.execute(f'SELECT * FROM fishyusers WHERE userid = {idtomodify}')
            afterdata = c.fetchone()
            await ctx.send(f"`Looks like that worked.\nOld values: {beforedata}\nNew values: {afterdata}`")
            conn.commit()
        except:
            allowedthings = """```
            userid = the users id (int)
            totalcaught = total number of fish caught (int)
            Level = the Level (int)
            trophyname = name of best fish caught (str)
            trophylength = length of best fish caught (str)[ex: "4.56cm"]
            guild = the guild id the user belongs to (int)
            hexcolor = the color that appears on their profile embed (str)
            reviewmsgid = the id of the review message the user submitted
            """
            await ctx.send(f"`Something went wrong! Valid values to modify:\n{allowedthings}")
            conn.commit()
    else:
        await ctx.send("`Insufficent permission.`")
        print(f"{ctx.message.author.name}({ctx.message.author.id}) tried to use ]setvalue in guild {ctx.message.guild.name}({ctx.message.guild.id})!")
        conn.commit()

@bot.command()
async def addguild(ctx):
    theguild = bot.get_guild(ctx.message.id)
    c.execute(f'SELECT * FROM fishyguilds WHERE guildid = {ctx.guild.id}')
    data = c.fetchone()
    if data == None:
        #(guildid text, guildtotal text, globalpos text, topuser text, guildtrophyname text, guildtrophylength text)''')
        c.execute(f"INSERT INTO fishyguilds VALUES ('{ctx.guild.id}','0','0','none','none')")
        await ctx.send("`I've added this guild to my database!`")
    else:
        await ctx.send("`Hmmm, i think this server is already in the database. If you believe this is wrong, please join our support server, using ]server`")
    conn.commit()

@bot.command()
async def help(ctx):
    await ctx.send(helpmsg)
    
@bot.command()
async def funnypicture(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/615010360348639243/702892395347312703/unknown.png")

@bot.command()
async def profile(ctx):
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    checkuser = usercheck(authorid)
    #(userid text, totalcaught text, Level text, rank text, trophyoid text, guild text, hexcolor text, reviewmsgid text)
    if checkuser is not False:
        returnedlist = getprofile(authorid,guildid,authorname)
        theirguildid = int(returnedlist[5])
        #print(theirguildid)
        returnedusersguild = bot.get_guild(theirguildid)

        embed = discord.Embed(title=f"**{authorname}**", description=f"*ID:{authorid}*", colour=discord.Colour(0x7a19fd))
        embed.set_author(name=f"User profile")
        embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
        embed.add_field(name="Total fish caught", value=f"{returnedlist[1]}", inline=False)
        users_levelandxp = returnedlist[2]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        print(levelmath)
        user_level = levelmath[0]
        embed.add_field(name="User Level", value=f"{int(user_level)}", inline=False)
        embed.add_field(name="XP",value=f"{levelmath[1]}",inline=False)
        embed.add_field(name="Trophy", value=f"{returnedlist[4]}", inline=False)
        embed.add_field(name="Guild", value=f"{returnedusersguild} (ID:{returnedlist[5]})", inline=False)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("`I was unable to retrieve your profile. Have you done ]start yet?`")
    conn.commit()

# @bot.command()
# async def profilecolor(ctx,hexcolor):
#     authorid = ctx.message.author.id
#     checkuser = usercheck(authorid)
#     hexcolor = "0x"+hexcolor
#     ##print(hexcolor)
#     checkuser = usercheck(authorid)
#     if checkuser == False:
#         await ctx.send("`I was unable to retrieve your profile. Have you done ]start yet?`")
#     else:
#         try:
#             embed = discord.Embed(title="<-- Theres a preview of your chosen color!", description=f"Are you sure you would like to change your profile color to hex value {hexcolor}?", colour=discord.Colour(hexcolor))
#             askmessage = await ctx.send(embed=embed)
#             await askmessage.add_reaction(emoji="\U00002705") # white check mark

#             def check(reaction, user):
#                 return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
#             try:
#                 reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
#             except asyncio.TimeoutError:
#                 pass
#             else:
#                 await ctx.send(f"`Success! Do {defaultprefix}profile to see your new profile color.`")
#         except:
#             embed = discord.Embed(title="An error has occured!", description=f"Please input a valid hex value. See [this color picker](https://htmlcolorcodes.com/color-picker/) if you need help.", colour=discord.Colour(0xfcd703))
#             embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
#             msgtoedit = await ctx.send(embed=embed)
#     conn.commit()

@bot.command()
async def start(ctx):
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    msgtoedit = await ctx.send("`Please wait...`")
    returnedmsg = addusers(authorid,guildid,guildname,authorname)
    await asyncio.sleep(0.2)
    await msgtoedit.edit(content=(returnedmsg))
    conn.commit()

@bot.command()
async def debug(ctx):
    authorid = ctx.message.author.id
    if int(authorid) == int(ownersID):
        c.execute(f"SELECT * FROM fishyusers")
        data = c.fetchall()
        await ctx.send(f"`{data}`")
        conn.commit()
    else:
        return "`ERROR: Missing permissions.`"
    authorid = ctx.message.author.id
@bot.command()
async def review(ctx, *, reviewtext):
    authorid = ctx.message.author.id
    authorname = ctx.message.author.id
    reviewchannel = bot.get_channel(reviewChannel_id)
    askmessage = await ctx.send("`Are you sure you would like to submit your review?`")
    await askmessage.add_reaction(emoji="\U00002705") # white check mark
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
    except asyncio.TimeoutError:
        pass
    else:
        c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
        data = c.fetchone()
        data = list(data)
        storedid = int(data[8])
        if storedid != 0:
            msgtoedit = bot.fetch_message(storedid)
            await msgtoedit.edit(f"`Heres a review from {authorname}({authorid}):```\n{reviewtext}```")
            await ctx.send(f"`Success! You've edited your review. If you think this was a mistake, and it shouldnt sent a message, please submit a issue on my github repo. The link can be found using {defaultprefix}info`")
        thereview = await reviewchannel.send(f"`Heres a review from {authorname}({authorid}):` ```\n{reviewtext}```")
        c.execute(f"Update fishyusers set reviewmsgid = {str(thereview)} where userid = {str(authorid)}")
        conn.commit()
        await ctx.send(f"`Success! You can edit your review at any time using this command.`")

@bot.command()
async def info(ctx):
    ping = bot.latency * 1000
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    embed = discord.Embed(title=f"**Info**", description="", colour=discord.Colour(0x158b94))
    embed.set_author(name=f"Requested by {authorname}")
    embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
    embed.add_field(name="Time started", value=time.strftime("%m-%d-%Y, %I:%M:%S EST",time_started), inline=False)
    embed.add_field(name="Fish caught since start", value=f"{fishCaughtInSession}", inline=False)
    embed.add_field(name="XP Gained in session",value = f"{xpGainedinsession}", inline=False)
    embed.add_field(name="Ping", value=f"{ping}", inline=False)
    embed.add_field(name="Github link", value="https://github.com/averwhy/fishy-discord-game", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print('------------------------------------------------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('------------------------------------------------')
    print(myname, version,"is connected and running")
    print('------------------------------------------------')
    conn.commit()

bot.run(TOKEN)