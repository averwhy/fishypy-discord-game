import discord
import aiohttp
import asyncio
import time
import random, math
import json
import re, os, sys
import platform
import aiosqlite
import traceback
import jishaku
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
#CONFIG#######################################################################################################
description = '''Fishy.py is an fork of Deda#9999's original Fishy bot. Fishy.py is being rewritten in discord.py API. To see commands use ]help. Full description on the fishy.py discord server: discord.gg/HSqevex'''
defaultprefix = ";"
secondstoReact = 7
ownersID = 267410788996743168
fishCaughtInSession = 0
xpGainedinsession = 0
commandsRun = 0
commandsActuallyRun = 0
reviewChannel_id = 735206051703423036
time_started = time.localtime()

#BOT#PARAMS###################################################################################################
TOKEN = ''
userid = '695328763960885269'
version = '0.9.9'
myname = "Fishy.py"
sinvite = "https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=355520&scope=bot"
bot = commands.Bot(command_prefix=["=",";"],description=description,intents=discord.Intents.all())
bot.remove_command('help')

#DB#MANAGEMENT################################################################################################
if os.path.isfile('fishypy.db'):
    db_exists = True
    print("Database found.")
else:
    print("Database not found! Bot will not start.")
#BOT#CODE#####################################################################################################

helpmsg = f"""```md
React on message to fish
Compete with others for best collection
#__________COMMANDS__________#
[{defaultprefix}start][register yourself to the db]
[{defaultprefix}fish|f][fish with Fishy.py]
[{defaultprefix}about][learn more about Fishy.py]
[{defaultprefix}profile|p][your profile and stats, or someone elses]
[{defaultprefix}trophy][your trophy, or someone elses]
[{defaultprefix}guild][view guild profile] < WIP >
[{defaultprefix}top|t (guilds,users)][Leaderboards]
[{defaultprefix}info][info and stats about bot]
[{defaultprefix}review][leave a review for the bot :) ]
[{defaultprefix}invite][invite bot to your server]
[{defaultprefix}support][join the fishy.py discord server]
[{defaultprefix}help|cmds][show this message]
```"""

async def grab_db_user(id):
    async with aiosqlite.connect("fishypy.db") as db:
        c = await db.execute('SELECT * FROM fishyusers WHERE userid = ?',(id,))
        data = await c.fetchone()
        await db.commit()
    return data

async def grab_db_guild(id):
    async with aiosqlite.connect("fishypy.db") as db:
        c = await db.execute('SELECT * FROM fishyguilds WHERE guildid = ?',(id,))
        data = await c.fetchone() 
    return data


class fishing:
    async def randomfish(self): # Returns a random fish from the database.
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute('SELECT * FROM fishes ORDER BY RANDOM() LIMIT 1;')
            data = await c.fetchone()
            await db.commit()
             
        return data
    async def getfish(self,oid):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(oid,))
            data = await c.fetchone()
            await db.commit()
             
        return data

class db_user:
    def __init__(self): #init func is useless because it cant be async Pepepains
        pass
    async def get_trophy(self,data):
        trophyoid = data[5]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(trophyoid,))
            returndata = await c.fetchone()
            await db.commit()
             
        return returndata
    def get_caughtfish(self,data):
        fishescaught = data[2]
        return fishescaught
    def get_level(self,data):
        x = float(data[3])
        usermath = divmod(x,1)
        userlevel = usermath[0]
        return userlevel
    def get_xp(self,data):
        xpmath = divmod(data[3],1)
        userxp = xpmath[1]
        return userxp
    def get_guild_obj(self,data):
        guildid = data[6]
        guildobj = bot.get_guild(guildid)
        return guildobj
    def get_review_id(self,data):
        reviewid = data[8]
        return reviewid
    ##Now for updates n stuff
    async def update_caught_fish(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            await db.commit()
             
        updatevalue = float(data[2])
        updatevalue += 1
        str(updatevalue)
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("Update fishyusers set totalcaught = ? where userid = ?",(updatevalue,userobject.id,))
            await db.commit()
             
        return
    async def check_trophy(self,data,caughtoid):
        usersid = data[0]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(caughtoid,))
            data2 = await c.fetchone()
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(data[5],))
            data = await c.fetchone()
            await db.commit()
        try:
            FishLengthFromTrophy = data[4]
            FishLengthJustCaught = data2[4]
            if float(FishLengthFromTrophy) < float(FishLengthJustCaught):
                async with aiosqlite.connect('fishypy.db') as db:
                    await db.execute("Update fishyusers set trophyoid = ? where userid = ?", (caughtoid, usersid,))
                    await db.commit()
                #print(FishLengthFromTrophy, "is smaller than", FishLengthJustCaught)
                return
            else:
                print(f"{FishLengthFromTrophy} vs {FishLengthJustCaught}")
        except:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("Update fishyusers set trophyoid = ? where userid = ?",(caughtoid,usersid,))
                await db.commit()
            print("user didnt have trophy so they got one")
            return
    async def add_user(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.name,))
            data = await c.fetchone()
            await db.commit()
            try:
                async with aiosqlite.connect('fishypy.db') as db:
                    await db.execute(f"INSERT INTO fishyusers VALUES (?,?,'0','0.00','0','None',?,'005dff','0')",(userobject.id,userobject.name,userobject.guild.id,))
                    await db.commit()
                return (f"`Done! Start fishing with {defaultprefix}fish, or view your profile with {defaultprefix}profile`")
            except Exception as e:
                return (f"`Something went wrong:` ```\n{e}\n```")
    async def update_review(self,userobject,r_id,reviewtext):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",userobject.id)
            data = await c.fetchone()
            await db.commit()
             
        if data is None:
            reviewchannel = bot.get_channel(reviewChannel_id)
            data = list(data)
            storedid = int(data[8])
            if storedid != 0:
                msgtoedit = await reviewchannel.fetch_message(int(storedid))
                await msgtoedit.edit(content=f"Heres a review from {userobject.mention} ({userobject.id}):```\n{reviewtext}```")
                return ("`Success! You've edited your review.")
            else:
                async with aiosqlite.connect('fishypy.db') as db:
                    await db.execute(f"Update fishyusers set reviewmsgid = {r_id} where userid = {userobject.id}")
                    await db.commit()
                     
                return (f"`Success! You can edit your review at any time using this command.`")
        else:
            return (f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")
        
    async def db_ban(self,userobject,reason):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            if data is not None:
                await db.execute("DELETE FROM fishyusers WHERE userid = ?",(userobject.id,))
                await db.commit()
                await db.execute(f"INSERT INTO bannedusers VALUES ('{userobject.id}','{userobject.name}','{reason}')")
                await db.commit()
                 
                return
            elif data is None:
                await db.execute(f"INSERT INTO bannedusers VALUES (?,?,?)",(userobject.id,userobject.name,reason,))
                await db.commit()
                 
            else:
                print("Something went wrong banning user")
                return
    async def db_unban(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            if data is not None:
                await db.execute(f"DELETE FROM bannedusers WHERE userid = ?",(userobject.id,))
                await db.commit()
    async def update_xp(self,userobject,rarity):
        global xpGainedinsession
        rarity = float(rarity)
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone() 
        theirlevel = data[3]
        updatevalue = round(float(rarity),3) #rounds xp
        theirlevel2 = divmod(updatevalue,1) #split up level and xp
        oldlevel = theirlevel2[0] #the level only, since divmod returns a tuple
        caughtxp = theirlevel2[1]
        ##################################
        xptoadd = caughtxp / 10
        xpGainedinsession += xptoadd
        updatevalue = float(theirlevel) + float(xptoadd)
        newlevel = divmod(float(updatevalue),1)
        newlevelint = int(newlevel[0])
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("UPDATE fishyusers SET Level = ? WHERE userid = ?",(updatevalue,userobject.id,))
            await db.commit()
        if newlevelint > int(oldlevel):
            return True
        else:
            return False
        # async with aiosqlite.connect('fishypy.db') as db:
        #     c = await db.execute("UPDATE fishyusers SET ",(userobject.id,))
        #     data = await c.fetchone()
            
            
class db_guild:
    #(guildid text, guildtotal text, globalpos text, topuser text, guildtrophyoid text)
    def __init__(self): #init func is useless because it cant be async Pepepains
        pass
    def get_caughtfish(self,data):
        return data[1]
    def get_trophy(self,data):
        return data[4]
    async def add_guild(self,guildobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyguilds WHERE guildid = ?",(guildobject.id,))
            data = await c.fetchone()
            if data is not None:
                await db.commit()
                 
                return
            else:
                await db.execute(f"INSERT INTO fishyguilds VALUES ('?','0','0','None','None')",(guildobject.id,))
                await db.commit()
                 
                return
    async def check_trophy(self,data,caughtOID):
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("SELECT * FROM fishyguilds WHERE guildid = ?",(data[0],))
    async def update_caught_fish(self,guildobj):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyguilds WHERE guildid = ?",(guildobj.id,))
            data = await c.fetchone()
            await db.commit()
             
        if data is None:
            return 
        if data is not None:
            updatevalue = int(data[1])
            updatevalue += 1
            str(updatevalue)
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("Update fishyguilds set guildtotal = ? where guildid = ?",(updatevalue,data[0]))
                await db.commit()
                 
        return
        
class bans:
    def __init__(self): #init func is useless because it cant be async Pepepains
        pass
    async def check_if_banned(self,idtocheck):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM bannedusers WHERE userid = ?",(idtocheck))
            data = await c.fetchone()
            await db.commit()
             
            if data is None:
                return False
            if data is not None:
                return True
    async def get_ban_reason(self,idtocheck):
        async with aiosqlite('fishypy.db') as db:
            c = await db.execute("SELECT * FROM bannedusers WHERE userid = ?",(idtocheck))
            data = await c.fetchone()
             
            if data is None:
                return "`That user is not banned!`"
            if data is not None:
                return data[2]
            

async def usercheck(authorid): # this function checks if the user exists in the DB
    async with aiosqlite.connect('fishypy.db') as db:
        c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(authorid,))
        data = await c.fetchone()
    if data is None:
         
        return False
    else:
         
        return True
    
async def fish_success_update(author,guild,rarity,oid,flength): # this runs when the user fishes (successfully)
    global fishCaughtInSession
    global xpGainedinsession
    
    dbguild = await grab_db_guild(guild.id)
    dbuser = await grab_db_user(author.id)
    
    user = db_user()
    await user.update_caught_fish(userobject=author)
    
    dbguild = db_guild()
    await dbguild.update_caught_fish(guildobj=guild)
    
    await user.check_trophy(data=dbuser,caughtoid=oid)
    
    await user.update_xp(userobject=author,rarity=rarity)
    
    # conn = aiosqlite.connect('fishypy.db')
    # c = conn.cursor()
    # updatevalue = None
    # c.execute(f'SELECT * FROM fishyusers WHERE userid = {authorid}')
    # data = c.fetchone()
    # data = list(data)
    # #level updates
    # theirlevel = data[3]
    # rarity = float(rarity)
    # theirlevel = float(theirlevel)
    # xptoadd = rarity / 10.0
    # xpGainedinsession += round(xptoadd,3)
    # updatevalue = theirlevel + xptoadd
    # str(updatevalue)
    # updatevalue = round(updatevalue,3)
    # c.execute(f"Update fishyusers set Level = {updatevalue} where userid = {authorid}")

    fishCaughtInSession += 1

def rodUpgradebar(rodlvl): # upgrade bar PogU Clap
    return f"{'#' * (decimal := round(rodlvl % 1 * 40))}{'_' * (40 - decimal)}"
    #print(returned_upgradeBar)

##############################################################################################
##############################################################################################
##############################################################################################

async def is_owner(ctx):
    return ctx.author.id == ownersID

@bot.event
async def on_command_error(ctx, error): # this is an event that runs when there is an error
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        #await ctx.message.add_reaction("\U00002753") # red question mark         
        pass
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown): 
        ohno =  str(discord.PartialEmoji(name="ohno", id=762137479317815318, animated=False))
        msgtodelete = await ctx.send(f"{ohno} `Youre on cooldown for {error.retry_after}s!`")
        await asyncio.sleep(10)
        await msgtodelete.delete()
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.send("`ERROR: Missing permissions.`")
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
    data = await grab_db_guild(guild.id)
    dbguild = db_guild()
    dbguild.add_guild(guild)

@bot.event
async def on_command(ctx):
    global commandsRun
    commandsRun += 1

@bot.event
async def on_command_completion(ctx):
    global commandsActuallyRun
    commandsActuallyRun += 1

@commands.cooldown(1,3,BucketType.user)
@bot.command(aliases=["f"])
async def fish(ctx): # the fishing command. this consists of 1. checking if the user exists 2. if user exists, put together an embed and get a fish from DB using fishing() func, 3. sends it and calls fish_update_success()
    channel = ctx.message.channel
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    checkuser = await usercheck(authorid)
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
            try:
                await msgtoedit.clear_reactions()
            except discord.errors.Forbidden:
                print(f"Failed to remove reactions in guild {ctx.message.guild.name} ({ctx.message.guild.id}), channel #{ctx.message.channel.name}")
        else:
            try:
                await msgtoedit.clear_reactions()
            except discord.errors.Forbidden:
                print(f"Failed to remove reactions in guild {ctx.message.guild.name} ({ctx.message.guild.id}), channel #{ctx.message.channel.name}")
            f = fishing()
            returnedlist = await f.randomfish()
            rarity = returnedlist[2]
            oid = returnedlist[0]
            flength = returnedlist[4]
            lvl_up_bool = await fish_success_update(author=ctx.author,guild=ctx.message.guild,rarity=rarity,oid=oid,flength=flength)
            if lvl_up_bool is True:
                await ctx.send(f"{ctx.author.mention}`, you leveled up!`")
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
            await msgtoedit.edit(embed=embed)
            print(f"{ctx.author.name} caught a {returnedlist[5]} in channel #{ctx.channel.name}, guild {ctx.guild.name} [user: {ctx.author.id}, channel {ctx.channel.id}, guild {ctx.guild.id}")

@commands.cooldown(1,10,BucketType.user)
@bot.command()
async def about(ctx):
    embed = discord.Embed(title=f"**About Fishy.py**", description="", colour=discord.Colour(0x158b94))
    embed.set_author(name=f"Developed by @averwhy#3899, Original by @Deda#6991")
    embed.set_footer(text=f"Made with Python {platform.python_version()}",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
    embed.add_field(name="What is Fishy.py?", value="Fishy.py is a fishing style game where you compete with other users or even guilds to have the best collection, or highest level, or fish. Originally created by Deda#9999 and written in JavaScript, Fishy was a huge success and is in over 1,000 servers. Sadly, it went offline as Deda could not host it anymore. But I (averwhy#3899) have recreated it, now better than ever!")
    embed.add_field(name="How does it work?", value="Fishy.py has a database with more than 16,000 fishes, thanks to https://www.fishbase.org ! All of them have unique images and names. When you fish, one is randomly selected from the database. However, in the future [v2], when you have a higher level you have a higher probability of catching more rare and uncommon fish!\nIn terms of technicality, Fishy.py is made with the `discord.py` API, which is a wrapper for the Discord API. Fishy.py also using `aiosqlite` for the database.")
    embed.add_field(name="Have more questions? Feel free to join the support server and ask averwhy#3899!", value=f"The servers invite can be obtained via the `{defaultprefix}support` command.",inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=["t"])
async def top(ctx,type): # command used to display top users, or top guilds
    ########################################################
    # THE FOLLOWING CODE INSIDE THIS COMMAND IS TRASH      #
    ########################################################
    type = type.lower()
    type = type.strip()
    #print(type)
    if type == "guilds":
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyguilds ORDER BY guildtotal DESC")
            data = await c.fetchmany(5)
            await db.commit()
             
        firstuser = data[0]
        seconduser = data[1]
        thirduser = data[2]
        fourthuser = data[3]
        fifthuser = data[4]
        
        guild1 = bot.get_guild(firstuser[3])
        guild2 = bot.get_guild(seconduser[3])
        guild3 = bot.get_guild(thirduser[3])
        guild4 = bot.get_guild(fourthuser[3])
        guild5 = bot.get_guild(fifthuser[3])

        embed = discord.Embed(title=f"**Leaderboard**", description=f"Sorted by: Guilds Fish total", colour=discord.Colour(0x7a19fd))
        embed.set_author(name=f"User profile")
        embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
        embed.add_field(name=f"1. {guild1.name} ({firstuser[0]})", value=f"Total caught: {firstuser[1]}", inline=False)
        embed.add_field(name=f"2. {guild2.name} ({seconduser[0]})", value=f"Total caught: {seconduser[1]}", inline=False)
        embed.add_field(name=f"3. {guild3.name} ({thirduser[0]})",value=f"Total caught: {thirduser[1]}",inline=False)
        embed.add_field(name=f"4. {guild4.name} ({fourthuser[0]})", value=f"Total caught: {fourthuser[1]}", inline=False)
        embed.add_field(name=f"5. {guild5.name} ({fourthuser[0]})", value=f"Total caught: {fifthuser[1]}", inline=False)
        #embed.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif type == "users":
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers ORDER BY Level DESC")
            data = await c.fetchmany(5)
            await db.commit()
             
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
        # print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"1. {firstuser[1]} [{firstuser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        users_levelandxp = seconduser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        # print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"2. {seconduser[1]} [{seconduser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        users_levelandxp = thirduser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        # print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"3. {thirduser[1]} [{thirduser[0]}]",value=f"Level {user_level[0]}, with {user_level[1]} XP",inline=False)
        users_levelandxp = fourthuser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        # print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"4. {fourthuser[1]} [{fourthuser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        users_levelandxp = fifthuser[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        # print(levelmath)
        user_level = levelmath
        embed.add_field(name=f"5. {fifthuser[1]} [{fifthuser[0]}]", value=f"Level {user_level[0]}, with {user_level[1]} XP", inline=False)
        #embed.set_thumbnail(url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"`I didnt recognize that keyword. Try:`\n`{defaultprefix}top users`\n`{defaultprefix}top guilds`")

@bot.command()
async def support(ctx): # this sends the fishypy support server link
    await ctx.send("`The support server's invite link is` http://discord.gg/HSqevex")

@commands.cooldown(1,30,BucketType.user)
@bot.command()
async def guild(ctx, id: int = None):
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    if id == None:
        data = await grab_db_user(authorid)
        returnedlist = await grab_db_guild(int(data[6]))
        async with aiosqlite.connect("fishypy.db") as db:
            c = await db.execute("SELECT * FROM (SELECT guildid, RANK() OVER (ORDER BY guildtotal DESC) AS guildtotal FROM fishyguilds) a WHERE guildid = '?';",(ctx.message.guild.id,)) # i love this statement
            data1 = await c.fetchone()
            c = await db.execute("SELECT * FROM fishyguilds")
            data2 = await c.fetchall()
            await db.commit()
             
        grabbedguild = bot.get_guild(int(data[6]))
        embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x242424))
        embed.set_footer(text=f"Fished by {authorname} | Fishy.py - {version}",icon_url=(ctx.author.avatar_url))
        embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")
        embed.add_field(name="Rank",value=f"#{data1[1]} out of {len(data2)} guilds")
        embed.set_image(url=grabbedguild.icon_url)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    await ctx.send(sinvite)

@bot.command(aliases=["cmds","cmd"])
async def help(ctx): # help message
    await ctx.send(helpmsg)
    
@bot.command()
async def funnypicture(ctx): # pretend this isnt here
    await ctx.send("https://cdn.discordapp.com/attachments/615010360348639243/702892395347312703/unknown.png")

@bot.command(aliases=["p"])
async def profile(ctx, user: discord.User = None): # profile command
    dbuser = db_user()
    tfish = fishing()
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    #(userid text, name text, totalcaught text, Level text, rank text, trophyoid text, guild text, hexcolor text, reviewmsgid text)
    if user == None:
        checkuser = await usercheck(authorid)
        if checkuser is not False:
            returnedlist = await grab_db_user(authorid)
            theirguildid = int(returnedlist[6])
            #print(theirguildid)
            returnedusersguild = bot.get_guild(theirguildid)

            embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x242424))
            embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")
            async with aiosqlite.connect("fishypy.db") as db:
                c = await db.execute(f"SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY Level DESC) AS Level FROM fishyusers) a WHERE userid = '{authorid}';") # i love this statement
                data1 = await c.fetchone()
                c = await db.execute("SELECT * FROM fishyusers")
                data2 = await c.fetchall()
                await db.commit()
                 
            embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} users")
            users_levelandxp = returnedlist[3]
            users_levelandxp = float(users_levelandxp)
            levelmath = divmod(users_levelandxp,1)
            # print(levelmath)
            user_level = levelmath[0]
            embed.add_field(name="User Level", value=f"{int(user_level)}")
            embed.add_field(name="XP",value=f"{levelmath[1]}")
            embed.add_field(name="Guild", value=f"{returnedusersguild.name} (ID:{returnedlist[6]})")
            trophyOID = returnedlist[5]
            tdata = await grab_db_user(authorid)
            data = await dbuser.get_trophy(data=tdata)
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
    else:
        authorid = user.id # this is the key difference between this else and if above
        checkuser = await usercheck(authorid)
        if checkuser is not False:
            returnedlist = await grab_db_user(authorid)
            theirguildid = int(returnedlist[6])
            #print(theirguildid)
            returnedusersguild = bot.get_guild(theirguildid)

            embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x242424))
            embed.set_footer(text=f"Fishy.py - {version}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")

            async with aiosqlite.connect("fishypy.db") as db:
                c = await db.execute(f"SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY Level DESC) AS Level FROM fishyusers) a WHERE userid = '{authorid}';") # i love this statement
                data1 = await c.fetchone()
                c = await db.execute("SELECT * FROM fishyusers")
                data2 = await c.fetchall()
                await db.commit()
                 
            embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} users")
            users_levelandxp = returnedlist[3]
            users_levelandxp = float(users_levelandxp)
            levelmath = divmod(users_levelandxp,1)
            # print(levelmath)
            user_level = levelmath[0]
            embed.add_field(name="User Level", value=f"{int(user_level)}")
            embed.add_field(name="XP",value=f"{levelmath[1]}")
            embed.add_field(name="Guild", value=f"{returnedusersguild.name} (ID:{returnedlist[6]})")
            trophyOID = returnedlist[5]
            tdata = await grab_db_user(authorid)
            trophyOID = dbuser.get_trophy(data=tdata)
            data = tfish.getfish(trophyOID)
            if data == None:
                tvalue = "You have no Trophy! Try fishing!"
            else:
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
            embed.add_field(name="Trophy", value=f"{tvalue}",inline=False)
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"`I was unable to retrieve that profile. They may not be in the database. Did you format that right?`")


# @bot.command()
# async def profilecolor(ctx,hexcolor): # WIP
#     authorid = ctx.message.author.id
#     checkuser = await usercheck(authorid)
#     hexcolor = "0x"+hexcolor
#     ##print(hexcolor)
#     checkuser = await usercheck(authorid)
#     if checkuser == False:
#         await ctx.send(f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")
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
async def start(ctx): # adds users to DB so they can fish
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    guildid = ctx.message.guild.id 
    guildname = ctx.message.guild.name
    data = await grab_db_user(authorid)
    if data is None:
        msgtoedit = await ctx.send("`Please wait...`")
        user = db_user()
        returnedmsg = await user.add_user(userobject=ctx.author)
        await asyncio.sleep(1) # to ease potential ratelimits
        await msgtoedit.edit(content=(returnedmsg))
    else:
        #user exists
        await ctx.send("`You're already in the database,`")

@bot.command()
@commands.check(is_owner)
async def debug(ctx): # debug stuff, depends whats in here. Owner only
    authorid = ctx.message.author.id
    caughtoid = "5ac88a68eadcdf42044615c0"
    data = ["267410788996743168"]
    async with aiosqlite.connect('fishypy.db') as db:
        await db.execute("Update fishyusers set trophyoid = ? where userid = ?", (caughtoid, data[0],))
        await db.commit()

@commands.cooldown(1,300,BucketType.user)
@bot.command()
async def review(ctx, *, reviewtext): # review command. Sends a message to fishypy guild and saves that message ID in db. If user has sent a review it checks for that and edits it if it exists.
    authorid = ctx.message.author.id
    authorname = ctx.message.author.name
    checkuser = await usercheck(authorid)
    if checkuser is not False:
        #fishyguild = bot.fetch_guild(734581170452430888)
        reviewchannel = bot.get_channel(735206051703423036)
        data = await grab_db_user(id=authorid)
        user = db_user()
        askmessage = await ctx.send("`Are you sure you would like to submit your review? If it contains inappropriate content, you will be banned from the bot.`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Prompt timed out. Try again`")
        else:
            thereview = await reviewchannel.send(f"Heres a review from {ctx.author.mention} ({ctx.author.id}):```\n{reviewtext}```")
            await user.update_review(userobject=ctx.author,r_id=thereview.id,reviewtext=reviewtext)
            
    else:
        await ctx.send(f"`I was unable to retrieve your profile. Have you done {defaultprefix}start yet?`")

@commands.cooldown(1,10,BucketType.user)
@bot.command()
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
@commands.check(is_owner)
async def stop(ctx):
    askmessage = await ctx.send("`Are you sure?`")
    await askmessage.add_reaction(emoji="\U00002705") # white check mark
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
    except asyncio.TimeoutError:
        await askmessage.edit(content="`Prompt timed out. Try again`")
    else:
        await askmessage.clear_reactions()
        await askmessage.edit(content="`Bye!`")
        print(f"Bot is being stopped by {ctx.message.author} ({ctx.message.id})")
        async with aiosqlite.connect('fishypy.db') as db: #useless lol
            await db.commit()
                
        await bot.logout()
@commands.cooldown(1,5,BucketType.user)
@bot.command()
async def trophy(ctx, user: discord.User = None):
    if user is None:
        authorid = ctx.message.author.id
        checkuser = await usercheck(authorid)
        if checkuser is not False:
            data1 = await grab_db_user(authorid)
            dbuser = db_user()
            data = await dbuser.get_trophy(data1)
            if data == None:
                embed = discord.Embed(title=f"You dont have a Trophy!",description="Try Fishing!")
            else: 
                embed = discord.Embed(title=f"{ctx.message.author.name}'s Trophy",colour=discord.Colour(0x00cc00))
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
                raritycalc = float(data[2])
                dbPos = data[3]
                raritycalc2 = None
                if raritycalc > 1.5:
                    raritycalc2 = "Legendary"
                elif raritycalc > 1.2:
                    raritycalc2 = "Rare"
                elif raritycalc > 0.7:
                    raritycalc2 = "Uncommon"
                elif raritycalc > 0:
                    raritycalc2 = "Common"
                embed.add_field(name=tvalue,value=f"{raritycalc2}({data[2]}), #{dbPos} in database")
            
            await ctx.send(embed=embed)
    elif user is not None:
        authorid = user.id
        checkuser = await usercheck(authorid)
        if checkuser is not False:
            data1 = await grab_db_user(authorid)
            dbuser = db_user()
            data = dbuser.get_trophy(data1)
            if data == None:
                embed = discord.Embed(title=f"You dont have a Trophy!",description="Try Fishing!")
            else: 
                embed = discord.Embed(title=f"{ctx.message.author.name}'s Trophy",colour=discord.Colour(0x00cc00))
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
                raritycalc = float(data[2])
                dbPos = data[3]
                raritycalc2 = None
                if raritycalc > 1.5:
                    raritycalc2 = "Legendary"
                elif raritycalc > 1.2:
                    raritycalc2 = "Rare"
                elif raritycalc > 0.7:
                    raritycalc2 = "Uncommon"
                elif raritycalc > 0:
                    raritycalc2 = "Common"
                embed.add_field(name=tvalue,value=f"{raritycalc2}({data[2]}), #{dbPos} in database")
            
            await ctx.send(embed=embed)

@bot.command()
@commands.check(is_owner)
async def sql(ctx, *, statement):
    try:
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute(statement)
            data = await c.fetchone()
            await db.commit()
        await ctx.send(data)
    except Exception as e:
        await ctx.send(f"```sql\n{e}\n```")

@bot.command()
@commands.check(is_owner)
async def userban(ctx, user1: discord.User = None, *, reason):
    if user1 == None:
        await ctx.send("`You must provide an user ID/Mention!`")
    else:
        data = await grab_db_user(user1.id)
        askmessage = await ctx.send(f"`User's info:` ```\n{data}\n``` `Banning user will reset data. Are you sure you want to ban {user1.name} ({user1.id})?`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=secondstoReact, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Prompt timed out.`")
        else:
            dbuser = db_user()
            dbuser.db_ban(userobject=user1,reason=reason)
            await ctx.send(f"`Banned {user1.name}{user1.id}!`")

@bot.command()
@commands.check(is_owner)
async def userunban(ctx,user: discord.User = None):
    if user == None:
        await ctx.send("`You must provide an user ID/Mention!`")
    else:
        await ctx.message.add_reaction("\U00002705")

@commands.cooldown(1,10,BucketType.user)
@bot.command()
async def loadjsk(ctx):
    try:
        bot.load_extension("jishaku")
        await ctx.send("`Done`")
    except Exception as e:
        await ctx.send(e)
    
@bot.command()
@commands.check(is_owner)
async def status(ctx, *, text):
    # Setting `Playing ` status
    try:
        await bot.change_presence(activity=discord.Game(name=text))
        await ctx.message.add_reaction("\U00002705")
    except:
        await ctx.message.add_reaction("\U0000274c")
   
newstext = "No news!"     
@bot.command()
async def news(ctx, *,setnews = None):
    global newstext
    if setnews == None:
        embed = discord.Embed(title="Fishy.py News",description=newstext,colour=discord.Colour(0x158b94))
        embed.set_footer(text=f"News set by {ctx.author.name}")
        await ctx.send(embed=embed)
    elif ctx.author.id == ownersID:
        newstext = setnews
        await ctx.message.add_reaction("\U00002705")
        await ctx.send("`News was set succesfully!`")
    else:
        await ctx.message.add_reaction("\U0000274c")
        await ctx.send("`Something went wrong. Make sure to provide no params while using news command`")

@bot.event
async def on_ready():
    time_started = time.localtime()
    print('-------------------------------------------------------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------------------------------------------------')
    print(myname, version,"is connected and running at",time.strftime("%m-%d-%Y, %I:%M:%S EST",time_started))
    print('-------------------------------------------------------')

bot.run(TOKEN)