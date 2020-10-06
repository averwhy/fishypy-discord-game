import discord
import aiohttp
import asyncio
import time
import random, math
import json
import re, os, sys
import platform
import sqlite3
import traceback
import jishaku
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
#CONFIG#######################################################################################################
description = '''Fishy.py is an fork of Deda#9999's original Fishy bot. Fishy.py is being rewritten in discord.py API. To see commands use ]help. Full description on the fishy.py discord server: discord.gg/HSqevex'''
defaultprefix = "="
secondstoReact = 7
ownersID = 267410788996743168
fishCaughtInSession = 0
xpGainedinsession = 0
commandsRun = 0
commandsActuallyRun = 0
reviewChannel_id = 735206051703423036

#BOT#PARAMS###################################################################################################
TOKEN = ''
userid = '695328763960885269'
version = '0.9.9'
myname = "Fishy.py"
sinvite = "https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=355520&scope=bot"
bot = commands.Bot(command_prefix=["=","`"],description=description,intents=discord.Intents.all())
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
             (userid text, name text, totalcaught text, Level text, rank text, trophyoid text, guild text, hexcolor text, reviewmsgid text)''') #i make them all text so its easier
             # userid = the users id (int)
             # totalcaught = total number of fish caught (int)
             # Level = the Level (int)
             # trophyname = name of best fish caught (str)
             # trophylength = length of best fish caught (str)[ex: "4.56cm"]
             # guild = the guild id the user belongs to (int)
             # hexcolor = the color that appears on their profile embed (str)
             # reviewmsgid = the id of the review message the user submitted
    c.execute("INSERT INTO fishyusers VALUES ('267410788996743168','0','0.00','0','none','0','005dff','0')") # this is me
    ############################################################################################################################
    c.execute('''CREATE TABLE fishyguilds
             (guildid text, guildtotal text, globalpos text, topuser text, guildtrophyoid text)''')
             #guildid = the guilds id (int)
             #guildtotal = total number of fish caught ever in guild (int)
             #globalpos = the guilds global position out of the rest of the guilds (int)
             #topuser = the guilds top user (int)
             #guildtrophyname = the guilds trophy fish, name (str)
             #guildtrophylength = the guilds trophy fish, length (str)
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
React on message to fish
Compete with others for best collection
#______COMMANDS______#
<default prefix="{defaultprefix}">
[fish|f][to start fishing]
[about][learn more about the bot]
[profile|p][player profile, Level, trophy, total caught]
[top|t (guilds,users)][Leaderboards] < WIP >
[info][info and stats about bot]
[review][leave a review for the bot :)]
[invite][invite bot to your discord server] < WIP >
[myguild][change the guild you belong to] < WIP >
[profilecolor|pc][change the embed color of your profile - TEMPORARILY DISABLED]
[support][join the fishy.py discord server]
[help|cmds][show this message]
```"""

def usercheck(authorid): # this function checks if the user exists in the DB
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    #print(data)
    if data is None:
        return False
    else:
        return True
def guildcheck(guildid): #for checking if guild exists in DB
    c.execute(f"SELECT * FROM fishyguilds WHERE ")

def fish_success_update(authorid,guildid,rarity,oid,flength): # this runs when the user fishes (successfully)
    global fishCaughtInSession
    global xpGainedinsession

    updatevalue = None
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    data = list(data)
    #level updates
    theirlevel = data[3]
    rarity = float(rarity)
    theirlevel = float(theirlevel)
    xptoadd = rarity / 10.0
    xpGainedinsession += round(xptoadd,3)
    updatevalue = theirlevel + xptoadd
    str(updatevalue)
    updatevalue = round(updatevalue,3)
    c.execute(f"Update fishyusers set Level = {updatevalue} where userid = {authorid}")

    #trophy check
    trophy_oid = data[5]
    print(oid)
    c.execute(f"SELECT * FROM fishes WHERE oid = '{trophy_oid}'")
    data = c.fetchone()
    if data == None:
        c.execute(f"UPDATE fishyusers SET trophyoid = '{oid}' WHERE userid = {authorid}")
    elif data[4] < flength:
        c.execute(f"UPDATE fishyusers SET trophyoid = '{oid}' WHERE userid = {authorid}")
    else:
        #runs when fish caught is smaller than trophy fish
        pass

    theirlevel = divmod(theirlevel,1)
    levelonly = theirlevel[0]
    newlevel = divmod(updatevalue,1)
    newlevelint = newlevel[0]
    if int(newlevelint) > int(levelonly):
        return True

    xptoadd = int(xptoadd)
    xpGainedinsession += xptoadd
    updatevalue = None

    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    data = list(data)

    updatevalue = int(data[2])
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

def rodUpgradebar(rodlvl): # upgrade bar PogU Clap
    return f"{'#' * (decimal := round(rodlvl % 1 * 40))}{'_' * (40 - decimal)}"
    #print(returned_upgradeBar)
    
def deluser(authorid,idtoremove): # this deletes an user from the DB
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

def addusers(authorid,guildid,guildname,authorname): # this adds users to the DB. runs when start command is called
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    if data is not None:
        return (f"`You're already in the database, {authorname}`")
    else:
        c.execute(f"INSERT INTO fishyusers VALUES ('{authorid}','{authorname}','0','0.00','0','None','{guildid}','005dff','0')")
        # (userid text, name text, totalcaught text, Level text, rank text, trophyoid text, guild text, hexcolor text, reviewmsgid text)
        returnmsg = (f"`Hey {authorname}, ive added you to the database! Start fishing with {defaultprefix}fish`")
        conn.commit()
    c.execute(f"SELECT * FROM fishyguilds WHERE guildid = {guildid}")
    data = c.fetchone()
    if data is None:
        print("the guild doesnt exist, so i shall add to database aswell")
        c.execute(f"INSERT INTO fishyguilds VALUES ('{guildid}','0','0','none','none')")
        conn.commit()
    return returnmsg

def getprofile(authorid): # this gets an user from the db, and returns a list with all their data
    c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    data = c.fetchone()
    authorid = int(authorid)
    ##print(data)
    if data is not None:
        return data
    else:
        return False #because they dont exist

def levelupcheck(authorid,lastxp): # this checks for levelling up when user fishes
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
async def on_command_error(ctx, error): # this is an event that runs when there is an error
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        #await ctx.message.add_reaction("\U00002753") # red question mark         
        pass
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown): 
        ohno =  str(discord.PartialEmoji(name="ohno", id=762137479317815318, animated=False))
        await ctx.send(f"{ohno} `Youre on cooldown!`")
    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.event
async def on_guild_remove(guild):
    logchannel = await bot.fetch_channel(761683999772377128)
    await logchannel.send(f"I am no longer in the `{guild.name} [{guild.id}]` guild")
@bot.event
async def on_guild_join(guild):
    logchannel = await bot.fetch_channel(761683999772377128)
    await logchannel.send(f"I am now in the `{guild.name} [{guild.id}]` guild!")
    c.execute(f"SELECT * FROM fishyguilds WHERE guildid = {guild.id}")
    data = c.fetchone()
    if data == None:
        c.execute(f"INSERT INTO fishyguilds VALUES ('{guild.id}','0','0','none','none')")

@bot.event
async def on_command(ctx):
    global commandsRun
    commandsRun += 1
    conn.commit()

@bot.event
async def on_command_completion(ctx):
    global commandsActuallyRun
    commandsActuallyRun += 1

@bot.command()
async def about(ctx):
    embed = discord.Embed(title=f"**About Fishy.py**", description="", colour=discord.Colour(0x158b94))
    embed.set_author(name=f"Developed by @averwhy#3899, Original by @Deda#9999")
    embed.set_footer(text=f"Made with Python {platform.python_version()}",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
    embed.add_field(name="What is Fishy.py?", value="Fishy.py is a fishing style game where you compete with other users or even guilds to have the best collection, or highest level, or fish. Originally created by Deda#9999 and written in JavaScript, Fishy was a huge success and is in over 1,000 servers. Sadly, it went offline as Deda could not host it anymore. But I (averwhy#3899) have recreated it, now better than ever!")
    embed.add_field(name="How does it work?", value="Fishy.py has a database with more than 16,000 fishes, thanks to https://www.fishbase.org ! All of them have unique images and names. When you fish, one is randomly selected from the database. However, in the future [v2], when you have a higher level you have a higher probability of catching more rare and uncommon fish!\nIn terms of technicality, Fishy.py is made with the `discord.py` API, which is a wrapper for the Discord API. Fishy.py also using `sqlite3` for the database.")
    embed.add_field(name="Have more questions? Feel free to join the support server and ask averwhy#3899!", value=f"The servers invite can be obtained via `{defaultprefix}support`",inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=["t"])
async def top(ctx,type): # command used to display top users, or top guilds
    ########################################################
    # THE FOLLOWING CODE INSIDE THIS COMMAND IS TRASH      #
    ########################################################
    type = type.lower()
    type = type.strip()
    print(type)
    if type == "guilds":
        c.execute("SELECT * FROM fishyguilds ORDER BY guildtotal DESC")
        data = c.fetchmany(5)
        firstuser = data[0]
        seconduser = data[1]
        thirduser = data[2]
        fourthuser = data[3]
        fifthuser = data[4]
            
        embed = discord.Embed(title=f"**Leaderboard**", description=f"Sorted by: Guilds Fish total", colour=discord.Colour(0x7a19fd))
        embed.set_author(name=f"User profile")
        embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
        embed.add_field(name=f"1.", value=f"{firstuser[3]}", inline=False)
        embed.add_field(name="2.", value=f"{seconduser[3]}", inline=False)
        embed.add_field(name="3.",value=f"{thirduser[3]}",inline=False)
        embed.add_field(name="4.", value=f"{fourthuser[3]}", inline=False)
        embed.add_field(name="5.", value=f"{fourthuser[3]}", inline=False)
        #embed.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif type == "users":
        c.execute("SELECT * FROM fishyusers ORDER BY Level DESC")
        data = c.fetchmany(5)
        firstuser = data[0]
        seconduser = data[1]
        thirduser = data[2]
        fourthuser = data[3]
        fifthuser = data[4]
        embed = discord.Embed(title=f"**Leaderboard**", description=f"Sorted by: User Level", colour=discord.Colour(0x00caff))
        embed.set_author(name=f"User profile")
        embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
        users_levelandxp = firstuser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"1. {firstuser[1]} [{firstuser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        users_levelandxp = seconduser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"2. {seconduser[1]} [{seconduser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        users_levelandxp = thirduser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"3. {thirduser[1]} [{thirduser[0]}]",value=f"Level {user_level[0]}, with {user_level[1]} XP",inline=False)
        users_levelandxp = fourthuser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"4. {fourthuser[1]} [{fourthuser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        users_levelandxp = fifthuser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"5. {fifthuser[1]} [{fifthuser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        #embed.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
        conn.commit()
    else:
        await ctx.send(f"`I didnt recognize that keyword. Try:`\n`{defaultprefix}top users`\n`{defaultprefix}top guilds`")

@commands.cooldown(1,3,BucketType.user)
@bot.command()
async def fish(ctx): # the fishing command. this consists of 1. checking if the user exists 2. if user exists, put together an embed and get a fish from DB using fishing() func, 3. sends it and calls fish_update_success()
    channel = ctx.message.channel
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    checkuser = usercheck(authorid)
    if checkuser == False:
        await ctx.send(f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")
    else:
        embed = discord.Embed(title=f"**React to fish!**", description="", colour=discord.Colour(0x000000))
        #embed.set_footer(text=f"Requested by {authorname} | Fishy.py - {version}",icon_url=(bot.user.avatar_url))
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
            oid = returnedlist[0]
            flength = returnedlist[4]
            lvl_up_bool = fish_success_update(authorid,guildid,rarity,oid,flength)
            if lvl_up_bool is not None:
                await ctx.send(f"`Hey `{ctx.author.mention}`, you leveled up!! Congrats!`")
            ##print(returnedlist)
            xp = float(returnedlist[2])
            xp2 = xp/100
            embed = discord.Embed(title=f"**{returnedlist[5]}**", description="",url=returnedlist[1], colour=discord.Colour(0x00cc00))
            embed.set_footer(text=f"Fished by {authorname} | Fishy.py - {version}",icon_url=(ctx.author.avatar_url))
            embed.add_field(name="__**XP Gained**__", value=f"{xp2}")
            raritycalc = float(returnedlist[2])
            raritycalc2 = None
            if raritycalc > 1.5:
                raritycalc2 = "Legendary"
            elif raritycalc > 1.2:
                raritycalc2 = "Rare"
            elif raritycalc > 0.7:
                raritycalc2 = "Uncommon"
            elif raritycalc > 0:
                raritycalc2 = "Common"
            embed.add_field(name="__**Rarity**__",value=f"{raritycalc2} ({returnedlist[2]})")
            embed.add_field(name="__**Length**__", value=f"{returnedlist[4]}cm")
            embed.add_field(name="__**# in database**__", value=f"{returnedlist[3]}/16205 fishes")
            embed.set_image(url=returnedlist[1])
            try:
                await msgtoedit.clear_reactions()
            except discord.errors.Forbidden:
                print(f"Failed to remove reactions in guild {ctx.message.guild.name} ({ctx.message.guild.id}), channel #{ctx.message.channel.name}")
            await asyncio.sleep(0.1)
            await msgtoedit.edit(embed=embed)
            
    conn.commit()

@bot.command()
async def support(ctx): # this sends the fishypy support server link
    await ctx.send("`The support server's invite link is` http://discord.gg/HSqevex")

@bot.command(aliases=["ru"])
async def removeuser(ctx,idtoremove): # this removes an user from the DB. Owner only
    authorid = ctx.message.author.id
    ylist = ["Y","yes","Yes","y","yEs"]
    idtoremove = int(idtoremove)
    userfromarg = await bot.fetch_user(idtoremove)
    await ctx.send(f"`Are you sure you want to remove {userfromarg}({idtoremove}) from the database? [Respond with Y]` ```diff\n- THIS DATA IS NOT RECOVERABLE. YOU WILL LOSE IT PERMANENTLY! -\n```")
        
    def check(m):
        return m.content in ylist and m.channel == ctx.message.channel
    msg = await bot.wait_for('message', timeout=secondstoReact,check=check)
    returnedmsg = deluser(authorid,idtoremove)
    await ctx.send(returnedmsg)
    conn.commit()

@bot.command()
async def invite(ctx):
    await ctx.send(sinvite)

@bot.command()
async def setvalue(ctx, idtomodify, valuetomodify, newvalue): # this sets certain values in the DB. Owner only
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

@bot.command(aliases=["ag"])
async def addguild(ctx, id): # this adds a guild to the db. Owner only
    if ctx.message.author.id == 267410788996743168:
        #theguild = bot.get_guild(ctx.message.id)
        #(guildid text, guildtotal text, globalpos text, topuser text, guildtrophyname text, guildtrophylength text)''')
        c.execute(f"INSERT INTO fishyguilds VALUES ('{id}','0','0','none','none')")
        await ctx.send(f"`I've added that guild to my database!`")
        conn.commit()
    else:
        await ctx.send("`Insufficent permission.`")
        print(f"{ctx.message.author.name}({ctx.message.author.id}) tried to use addguild in guild {ctx.message.guild.name}({ctx.message.guild.id})!")
        conn.commit()

@bot.command(aliases=["cmds","cmd"])
async def help(ctx): # help message
    await ctx.send(helpmsg)
    
@bot.command()
async def funnypicture(ctx): # pretend this isnt here
    await ctx.send("https://cdn.discordapp.com/attachments/615010360348639243/702892395347312703/unknown.png")

@bot.command(aliases=["p"])
async def profile(ctx, member: discord.Member = None): # profile command
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    #(userid text, name text, totalcaught text, Level text, rank text, trophyoid text, guild text, hexcolor text, reviewmsgid text)
    if member == None:
        checkuser = usercheck(authorid)
        if checkuser is not False:
            returnedlist = getprofile(authorid)
            theirguildid = int(returnedlist[6])
            #print(theirguildid)
            returnedusersguild = bot.get_guild(theirguildid)

            embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x242424))
            embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")

            c.execute(f"SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY Level DESC) AS Level FROM fishyusers) a WHERE userid = '{authorid}';") # i love this statement
            data1 = c.fetchone()
            c.execute("SELECT * FROM fishyusers")
            data2 = c.fetchall()
            embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} users")
            users_levelandxp = returnedlist[3]
            users_levelandxp = float(users_levelandxp)
            levelmath = divmod(users_levelandxp,1)
            print(levelmath)
            user_level = levelmath[0]
            embed.add_field(name="User Level", value=f"{int(user_level)}")
            embed.add_field(name="XP",value=f"{levelmath[1]}")
            embed.add_field(name="Guild", value=f"{returnedusersguild.name} (ID:{returnedlist[6]})")
            trophyOID = returnedlist[5]
            c.execute(f"SELECT * FROM fishes WHERE oid = '{trophyOID}'")
            tvalue = ""
            data = c.fetchone()
            if data == None:
                tvalue = "You have no Trophy! Try fishing!"
            else:
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
            embed.add_field(name="Trophy", value=f"{tvalue}",inline=False)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")
        conn.commit()
    else:
        authorid = member.id
        checkuser = usercheck(authorid)
        if checkuser is not False:
            returnedlist = getprofile(authorid)
            theirguildid = int(returnedlist[6])
            #print(theirguildid)
            returnedusersguild = bot.get_guild(theirguildid)

            embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x242424))
            embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")

            c.execute(f"SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY Level DESC) AS Level FROM fishyusers) a WHERE userid = '{authorid}';") # i love this statement
            data1 = c.fetchone()
            c.execute("SELECT * FROM fishyusers")
            data2 = c.fetchall()
            embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} users")
            users_levelandxp = returnedlist[3]
            users_levelandxp = float(users_levelandxp)
            levelmath = divmod(users_levelandxp,1)
            print(levelmath)
            user_level = levelmath[0]
            embed.add_field(name="User Level", value=f"{int(user_level)}", inline=False)
            embed.add_field(name="XP",value=f"{round(levelmath[1],3)}")
            embed.add_field(name="Trophy", value=f"{returnedlist[5]}")
            embed.add_field(name="Guild", value=f"{returnedusersguild.name} (ID:{returnedlist[6]})", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"`I was unable to retrieve that profile. They may not be in the database. Did you format that right?`")
        conn.commit()


@bot.command()
async def profilecolor(ctx,hexcolor): # WIP
    authorid = ctx.message.author.id
    checkuser = usercheck(authorid)
    hexcolor = "0x"+hexcolor
    ##print(hexcolor)
    checkuser = usercheck(authorid)
    if checkuser == False:
        await ctx.send(f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")
    else:
        try:
            embed = discord.Embed(title="<-- Theres a preview of your chosen color!", description=f"Are you sure you would like to change your profile color to hex value {hexcolor}?", colour=discord.Colour(hexcolor))
            askmessage = await ctx.send(embed=embed)
            await askmessage.add_reaction(emoji="\U00002705") # white check mark

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
            except asyncio.TimeoutError:
                pass
            else:
                await ctx.send(f"`Success! Do {defaultprefix}profile to see your new profile color.`")
        except:
            embed = discord.Embed(title="An error has occured!", description=f"Please input a valid hex value. See [this color picker](https://htmlcolorcodes.com/color-picker/) if you need help.", colour=discord.Colour(0xfcd703))
            embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
            msgtoedit = await ctx.send(embed=embed)
    conn.commit()

@bot.command()
async def start(ctx): # adds users to DB so they can fish
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    msgtoedit = await ctx.send("`Please wait...`")
    returnedmsg = addusers(authorid,guildid,guildname,authorname)
    await asyncio.sleep(1)
    await msgtoedit.edit(content=(returnedmsg))
    conn.commit()

@bot.command()
async def debug(ctx): # debug stuff, depends whats in here. Owner only
    authorid = ctx.message.author.id
    if int(authorid) == int(ownersID):
        # await ctx.send("`Nothing is specified to debug.`")
        c.execute(f"DROP TABLE fishyguilds")
        data = c.fetchall()
        await ctx.message.add_reaction(emoji="\U00002705")
        await ctx.send(data)
    else:
        await ctx.send("`Missing permissions.`")
    authorid = ctx.message.author.id
@bot.command()
async def review(ctx, *, reviewtext): # review command. Sends a message to fishypy guild and saves that message ID in db. If user has sent a review it checks for that and edits it if it exists.
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    checkuser = usercheck(authorid)
    if checkuser is not False:
        #fishyguild = bot.fetch_guild(734581170452430888)
        reviewchannel = bot.get_channel(reviewChannel_id)
        askmessage = await ctx.send("`Are you sure you would like to submit your review? If it contains inappropriate content, you will be banned from the bot.`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Prompt timed out. Try again`")
        else:
            c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
            data = c.fetchone()
            data = list(data)
            storedid = int(data[8])
            if storedid != 0:
                msgtoedit = await reviewchannel.fetch_message(int(storedid))
                await msgtoedit.edit(content=f"Heres a review from {ctx.author.mention} ({authorid}):```\n{reviewtext}```")
                await askmessage.edit(content=f"`Success! You've edited your review. If you think this was a mistake, and it shouldnt sent a message, please submit a issue on my github repo. The link can be found using {defaultprefix}info`")
            else:
                thereview = await reviewchannel.send(f"Heres a review from {ctx.author.mention} ({authorid}):```\n{reviewtext}```")
                c.execute(f"Update fishyusers set reviewmsgid = {thereview.id} where userid = {authorid}")
                conn.commit()
                await askmessage.edit(content=f"`Success! You can edit your review at any time using this command.`")
    else:
        await ctx.send(f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")

@bot.command(aliases=["vp"])
async def viewprofile(ctx, idtoview):
    idtoview = idtoview.strip()
    authorid = idtoview
    # try:
    if True:
        checkuser = usercheck(authorid)
        if checkuser is not False:
            userobj = await bot.fetch_user(authorid)
            returnedlist = getprofile(authorid)
            theirguildid = int(returnedlist[6])
            #print(theirguildid)
            returnedusersguild = bot.get_guild(theirguildid)

            embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x7a19fd))
            embed.set_author(name=f"User profile")
            embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")

            c.execute(f"SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY Level DESC) AS Level FROM fishyusers) a WHERE userid = '{authorid}';") # i love this statement
            data1 = c.fetchone()
            c.execute("SELECT * FROM fishyusers")
            data2 = c.fetchall()
            embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} users")
            users_levelandxp = returnedlist[3]
            users_levelandxp = float(users_levelandxp)
            levelmath = divmod(users_levelandxp,1)
            print(levelmath)
            user_level = levelmath[0]
            embed.add_field(name="User Level", value=f"{int(user_level)}", inline=False)
            embed.add_field(name="XP",value=f"{levelmath[1]}")
            embed.add_field(name="Trophy", value=f"{returnedlist[5]}")
            embed.add_field(name="Guild", value=f"{returnedusersguild.name} (ID:{returnedlist[6]})", inline=False)
            embed.set_thumbnail(url=userobj.avatar_url)
            await ctx.send(embed=embed)
    # except:
    #     await ctx.send(f"`Something went wrong. Make sure its formatted correctly, e.g:` `{defaultprefix}viewprofile 267410788996743168`")

@bot.command(aliases=[""])
async def info(ctx): # info thing
    ping = bot.latency * 1000
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    embed = discord.Embed(title=f"**Info**", description="", colour=discord.Colour(0x158b94))
    embed.set_author(name=f"Requested by {authorname}")
    embed.set_footer(text=f"Made with Python {platform.python_version()}, {platform.python_branch()} branch",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
    embed.add_field(name="Time started", value=time.strftime("%m-%d-%Y, %I:%M:%S EST",time_started))
    embed.add_field(name="Fish caught since start", value=f"{fishCaughtInSession}")
    embed.add_field(name="XP Gained in session",value = f"{round(xpGainedinsession,3)}")
    embed.add_field(name="Commands run in session",value=commandsRun)
    embed.add_field(name="Commands run, in session, successfully",value=commandsActuallyRun)
    embed.add_field(name="Discord.py version",value=discord.__version__,inline=False)
    embed.add_field(name="Ping", value=f"{round(ping, 3)}", inline=False)
    embed.add_field(name="Github link", value="https://github.com/averwhy/fishy-discord-game", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def stop(ctx):
    if ctx.author.id != ownersID:
        await ctx.send("`Nice try. Owner only PepeLaugh`")
    else:
        askmessage = await ctx.send("`Are you sure?`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Prompt timed out. Try again`")
        else:
            await ctx.send("`Bye!`")
            print(f"Bot is being stopped by {ctx.message.author} ({ctx.message.id})")
            conn.commit()
            conn.close()
            await bot.logout()

@bot.command()
async def sql(ctx, *, statement):
    if ctx.author.id != ownersID:
        await ctx.send("`Did you really think i wouldnt make the command that runs SQL statements, owner only? lol [Access Denied]`")
    else:
        try:
            c.execute(statement)
            data = c.fetchone()
            await ctx.send(data)
        except Exception as e:
            await ctx.send(e)

@bot.command()
async def loadjsk(ctx):
    bot.load_extension("jishaku")
    await ctx.send("`Done`")

@bot.event
async def on_ready():
    print('-------------------------------------------------------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------------------------------------------------')
    print(myname, version,"is connected and running at",time.strftime("%m-%d-%Y, %I:%M:%S EST",time_started))
    print('-------------------------------------------------------')
    conn.commit()

bot.run(TOKEN)