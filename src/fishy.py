# pylint: disable=wrong-import-order, missing-function-docstring, invalid-name, broad-except, too-many-branches, too-many-statements, too-many-locals, 

import platform
import traceback
import asyncio
import time
import os, sys
import aiosqlite
import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
#CONFIG#######################################################################################################
description = '''Fishy.py is an fork of Deda#9999's original Fishy bot. Fishy.py is being rewritten in discord.py API. To see commands use ]help. Full description on the fishy.py discord server: discord.gg/HSqevex'''
ownersID = 267410788996743168
reviewChannel_id = 735206051703423036

#BOT##########################################################################################################
class bot(commands.Bot):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
    async def usercheck(self, authorid): # this function checks if the user exists in the DB
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(authorid,))
            data = await c.fetchone()
        if data is None:
            return False
        else:
            return True
    
    async def guildcheck(self, guildid): # this function checks if the user exists in the DB
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyguilds WHERE guildid = ?",(guildid,))
            data = await c.fetchone()
        if data is None:   
            return False
        else:
            return True
        
    async def grab_db_user(self, id):
        async with aiosqlite.connect("fishypy.db") as db:
            c = await db.execute('SELECT * FROM fishyusers WHERE userid = ?',(id,))
            data = await c.fetchone()
            await db.commit()
        return data

    async def grab_db_guild(self, id):
        async with aiosqlite.connect("fishypy.db") as db:
            c = await db.execute('SELECT * FROM fishyguilds WHERE guildid = ?',(id,))
            data = await c.fetchone() 
            await db.commit()
        return data
        
with open("TOKEN.txt",'r') as t:
    TOKEN = t.readline()
userid = '695328763960885269'
myname = "Fishy.py"
sinvite = "https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot"
#bot = commands.Bot(command_prefix=["=",";","f!","fishy "],description=description,intents=discord.Intents(reactions = True, messages = True, guilds = True, members = True))
bot = commands.Bot(command_prefix=commands.when_mentioned_or('fishy ', 'fpy ','f!','='),description=description,intents=discord.Intents(reactions = True, messages = True, guilds = True, members = True))
bot.remove_command('help')
initial_extensions = ['cogs.funnypicture','cogs.FishyServerTools','cogs.Meta','jishaku']

#BOT#VARS#####################################################################################################
bot.time_started = time.localtime()
bot.launch_time = datetime.utcnow()
bot.version = '1.0.4'
bot.newstext = None
bot.news_set_by = "no one yet.."
bot.socket_sent_counter = 0
bot.socket_recieved_counter = 0
bot.fishCaughtinsession = 0
bot.xpgainedinsession = 0
bot.commandsRun = 0
bot.commandsFailed = 0
bot.defaultprefix = "="
bot.xp_multiplier = 1.0
bot.secondstoReact = 7
##############################################################################################################
helpmsg = f"""```md
React on message to fish
Compete with others for best collection
#__________COMMANDS__________#
[{bot.defaultprefix}start][register yourself to the db]
[{bot.defaultprefix}fish|f][fish with Fishy.py]
[{bot.defaultprefix}about][learn more about Fishy.py]
[{bot.defaultprefix}profile|prof][your profile and stats, or someone elses]
[{bot.defaultprefix}trophy][your trophy, or someone elses]
[{bot.defaultprefix}guild][view guild profile]
[{bot.defaultprefix}top|t (guilds,users)][user and guild leaderboards]
[{bot.defaultprefix}info][info and stats about bot]
[{bot.defaultprefix}ping][show my latency to discord]
[{bot.defaultprefix}review][leave a review for the bot :) ]
[{bot.defaultprefix}invite][invite bot to your server]
[{bot.defaultprefix}support][join the fishy.py discord server]
[{bot.defaultprefix}help|cmds][show this message]
```"""

############################################################################################################################################################################################
############################################################################################################################################################################################
############################################################################################################################################################################################

async def is_owner(ctx):
    return ctx.author.id == ownersID

class BanCheckError(CheckFailure):
    pass

async def ban_check(ctx):
    async with aiosqlite.connect('fishypy.db') as db:
        c = await db.execute("SELECT * FROM bannedusers WHERE userid = ?",(ctx.author.id,))
        data = await c.fetchone()
    if data is None: # If none, user is not banned 
        return True
    raise BanCheckError()

class IsNotInGuild(CheckFailure):
    pass

async def is_in_guild(ctx):
    if ctx.guild is None:
        raise IsNotInGuild()
    else:
        return True

@bot.event
async def on_guild_join(guild):
    logchannel = bot.get_channel(761683999772377128)
    if logchannel is None:
        logchannel = await bot.fetch_channel(761683999772377128)
    msg = f"""Im now in this guild: ```prolog
Guild:           {guild.name}
ID:              {guild.id}
Owner:           {str(guild.owner)}
Region:          {guild.region}
Members:         {guild.member_count}
Boosters:        {len(guild.premium_subscribers)}
Boost level:     {guild.premium_tier}
Channels:        {len(guild.channels)}
Roles:           {len(guild.roles)}
Filesize limit:  {guild.filesize_limit}
Desc:            {(guild.description or 'None')}
Created:         {guild.created_at}
Emoji limit:     {guild.emoji_limit}```
            """
    await logchannel.send(msg)
@bot.event
async def on_guild_remove(guild):
    logchannel = bot.get_channel(761683999772377128)
    if logchannel is None:
        logchannel = await bot.fetch_channel(761683999772377128)
    msg = f"""Im no longer in this guild: ```prolog
Guild:           {guild.name}
ID:              {guild.id}
Owner:           {str(guild.owner)}
Region:          {guild.region}
Members:         {guild.member_count}
Boosters:        {len(guild.premium_subscribers)}
Boost level:     {guild.premium_tier}
Channels:        {len(guild.channels)}
Roles:           {len(guild.roles)}
Filesize limit:  {guild.filesize_limit}
Desc:            {(guild.description or 'None')}
Created:         {guild.created_at}
Emoji limit:     {guild.emoji_limit}```
            """
    await logchannel.send(msg)

@bot.event
async def on_command(ctx):
    bot.commandsRun += 1

@bot.command(aliases=["cmds","cmd","command","commands","?"])
async def help(ctx): # hardcoded help OMEGALUL
    await ctx.send(helpmsg)

@bot.command()
async def invite(ctx):
    await ctx.send(f"<{sinvite}>")

@bot.command()
@commands.check(ban_check)
@commands.check(is_owner)
async def debug(ctx): # debug stuff, depends whats in here. Owner only
    authorid = ctx.message.author.id
    caughtoid = "5ac88a68eadcdf42044615c0"
    data = ["267410788996743168"]
    async with aiosqlite.connect('fishypy.db') as db:
        await db.execute("Update fishyusers set trophyoid = ? where userid = ?", (caughtoid, data[0],))
        await db.commit()
   
@commands.check(is_owner)
@bot.group(invoke_without_command=True)
async def dev(ctx):
    #bot dev commands
    await ctx.send("`You're missing one of the below arguements:` ```md\n- reload\n- loadall\n- status <reason>\n- ban <user> <reason>\n```")

@dev.command(aliases=["r","reloadall"])
@commands.check(is_owner)
async def reload(ctx):
    output = ""
    amount_reloaded = 0
    async with ctx.channel.typing():
        for e in initial_extensions:
            try:
                bot.reload_extension(e)
                amount_reloaded += 1
            except Exception as e:
                e = str(e)
                output = output + e + "\n"
        await asyncio.sleep(1)
        if output == "":
            await ctx.send(content=f"`{len(initial_extensions)} cogs succesfully reloaded.`") # no output = no error
        else:
            await ctx.send(content=f"`{amount_reloaded} cogs were reloaded, except:` ```\n{output}```") # output

@dev.command(aliases=["load","l"])
@commands.check(is_owner)
async def loadall(ctx):
    output = ""
    amount_loaded = 0
    async with ctx.channel.typing():
        for e in initial_extensions:
            try:
                bot.load_extension(e)
                amount_loaded += 1
            except Exception as e:
                e = str(e)
                output = output + e + "\n"
        await asyncio.sleep(1)
        if output == "":
            await ctx.send(content=f"`{len(initial_extensions)} cogs succesfully loaded.`") # no output = no error
        else:
            await ctx.send(content=f"`{amount_loaded} cogs were loaded, except:` ```\n{output}```") # output

@commands.check(is_in_guild)
@dev.command()
@commands.check(is_owner)
async def status(ctx, *, text):
    # Setting `Playing ` status
    if text is None:
        await ctx.send(f"{ctx.guild.me.status}")
    if len(text) > 60:
        await ctx.send("`Too long you pepega`")
        return
    try:
        await bot.change_presence(activity=discord.Game(name=text))
        await ctx.message.add_reaction("\U00002705")
    except Exception as e:
        await ctx.message.add_reaction("\U0000274c")
        await ctx.send(f"`{e}`")
        
@dev.command(aliases=["userban"])
@commands.check(is_owner)
async def ban(ctx, user1: discord.User = None, *, reason = None):
    if user1 is None:
        await ctx.send("`You must provide an user ID/Mention!`")
    else:
        data = await grab_db_user(user1.id)
        askmessage = await ctx.send(f"`Are you sure you want to ban` {user1.name} `({user1.id})?`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Timed out.`")
        else:
            dbuser = db_user()
            await dbuser.db_ban(userobject=user1,reason=reason)
            await ctx.send(f"`Banned {user1.name}!`")
            banlogs = bot.get_channel(771008991748554775)
            if banlogs is None:
                banlogs = await bot.fetch_channel(771008991748554775)
            await banlogs.send(f"__**User ban**__\n**User:** {str(user1)}\n**ID:** {user1.id}\n**Reason:** {reason}\n \n**Banned by:** {ctx.author.mention}")

@dev.command(aliases=["userunban"])
@commands.check(is_owner)
async def unban(ctx,user: discord.User = None):
    if user is None:
        await ctx.send("`You must provide an user ID/Mention!`")
    else:
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM bannedusers WHERE userid = ?",(user.id,))
            data = await c.fetchone()
            if data is None:
                await ctx.send("`That user does not appear to be banned.`")
            else:
                await db.execute("DELETE FROM bannedusers WHERE userid = ?",(user.id,))
                await db.commit()
                banlogs = bot.get_channel(771008991748554775)
                if banlogs is None:
                    banlogs = await bot.fetch_channel(771008991748554775)
                await banlogs.send(f"__**User unban**__\n**User:** {str(user)}\n**ID:** {user.id}\n \n**Unbanned by:** {ctx.author.mention}")
                await ctx.message.add_reaction("\U00002705")

@dev.command()
@commands.check(is_owner)
async def stop(ctx):
    askmessage = await ctx.send("`you sure?`")
    def check(m):
        newcontent = m.content.lower()
        return newcontent == 'yea' and m.channel == ctx.channel
    try:
        await bot.wait_for('message', timeout=bot.secondstoReact, check=check)
    except asyncio.TimeoutError:
        await askmessage.edit(content="`Timed out. haha why didnt you respond you idiot`")
    else:
        await askmessage.clear_reactions()
        await ctx.send("`bye`")
        print(f"Bot is being stopped by {ctx.message.author} ({ctx.message.id})")
        await bot.logout()
        
@dev.command(aliases=["rc"])
@commands.check(is_owner)
async def resetcooldown(ctx, *cmdnames):
    output = ""
    if "all" in cmdnames:
        for c in bot.commands:
            try:
                c._buckets._cooldown.reset()
                output = output + (f"Cooldown on command {c.name} successfully reset") + "\n"
            except Exception as e:
                e = str(e)
                output = output + e + "\n"
    else:
        for c in cmdnames:
            try:
                cmd = bot.get_command(c)       
                cmd._buckets._cooldown.reset()
                output = output + (f"Cooldown on command {cmd.name} successfully reset") + "\n"
            except Exception as e:
                e = str(e)
                output = output + e + "\n"
    await ctx.send(f"```{output}\n```")
    
@dev.group(invoke_without_command=True)
@commands.check(is_owner)
async def sql(ctx):
    await ctx.send("`Youre missing one of the below params:` ```md\n- fetchone\n- fetchall\n- run\n```") 
        
@sql.command()
async def fetchone(ctx, *, statement):
    try:
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute(statement)
            data = await c.fetchone()
            await db.commit()
        await ctx.send(data)
    except Exception as e:
        await ctx.send(f"```sql\n{e}\n```")
        
@sql.command()
async def fetchall(ctx, *, statement):
    try:
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute(statement)
            data = await c.fetchall()
            await db.commit()
        await ctx.send(data)
    except Exception as e:
        await ctx.send(f"```sql\n{e}\n```")
@sql.command()
async def run(ctx, *, statement):
    try:
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute(statement)
            await db.commit()
        await ctx.message.add_reaction(emoji="\U00002705")
    except Exception as e:
        await ctx.send(f"```sql\n{e}\n```") 
    
@bot.event
async def on_ready():
    print('-------------------------------------------------------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------------------------------------------------')
    print(myname, bot.version,"is connected and running at",time.strftime("%m-%d-%Y, %I:%M:%S EST",bot.time_started))
    print('-------------------------------------------------------')

for cog in initial_extensions:
    try:
        bot.load_extension(f"{cog}")
        print(f"loaded {cog}")
    except Exception as e:
        print(f"Failed to load {cog}, error:\n", file=sys.stderr)
        traceback.print_exc()
asyncio.set_event_loop(asyncio.SelectorEventLoop())
bot.run(TOKEN, bot = True, reconnect = True)
