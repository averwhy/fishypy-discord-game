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

from cogs.utils import player, server, fish, botchecks
#BOT##########################################################################################################
class MyContext(commands.Context):
    #self = ctx
    async def send_in_codeblock(self, content, *, language: str = None):
        if language is None:
            lang = ''
        else:
            lang = language
        await self.send(f"```{lang}\n{content}```")
        
    async def random_fish(self):
        # self = ctx
        # So self.bot == ctx.bot
        c = await self.bot.db.execute("SELECT * FROM fishes ORDER BY RANDOM()")
        data = await c.fetchone()
        fishobject = fish.fish(data)
        return fishobject

class fpybot(commands.Bot): # Subclass of bot to give us methods
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)
    
    async def usercheck(self, authorid): # this function checks if the user exists in the DB
        c = await self.db.execute("SELECT * FROM fishes ORDER BY RANDOM()")
        data = await c.fetchone()
        if not data:
            return False
        return True
        
    async def grab_db_user(self, uid):
        c = await self.db.execute("SELECT * FROM f_users WHERE userid = ?",(uid,))
        data = await c.fetchone()
        return data
    
    async def randomfish(self): # Returns a random fish from the database.
        c = await self.db.execute('SELECT * FROM fishes ORDER BY RANDOM() LIMIT 1;')
        data = await c.fetchone()
        await self.db.commit()
        return data
    
    async def rodUpgradebar(self, rodlvl):
        return f"{'#' * (decimal := round(rodlvl % 1 * 15))}{'_' * (15 - decimal)}"
    #print(returned_upgradeBar)   

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"  
with open("TOKEN.txt",'r') as t:
    TOKEN = t.readline()
userid = '695328763960885269'
myname = "Fishy.py"
sinvite = "https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot"
defaultprefix = '!!'
async def get_prefix(bot, message):
    return bot.prefixes.get(message.guild.id, defaultprefix)
bot = fpybot(command_prefix=get_prefix,intents=discord.Intents(reactions = True, messages = True, guilds = True, members = True))
bot.remove_command('help')
initial_extensions = ['jishaku', 'cogs.owner', 'cogs.funnypicture', 'cogs.FishyServerTools', 'cogs.meta', 'cogs.events', 'cogs.game', 'cogs.newhelp']

#BOT#VARS#####################################################################################################
bot.ownerID = 267410788996743168
bot.reviewChannel_id = 735206051703423036
bot.launch_time = datetime.utcnow()
bot.version = '1.1.0'
bot.newstext = None
bot.news_set_by = "no one yet.."
bot.socket_sent_counter = 0
bot.socket_recieved_counter = 0
bot.fishCaughtinsession = 0
bot.commandsRun = 0
bot.commandsFailed = 0
bot.defaultprefix = defaultprefix
bot.coin_multiplier = 1.0
bot.secondstoReact = 7
bot.fishers = []
bot.coinsearned = 0
bot.rodsbought = 0
async def startup(bot):
    bot.db = await aiosqlite.connect('fpy.db')
    await bot.db.execute('CREATE TABLE IF NOT EXISTS f_prefixes (guildid int, prefix text)')
    await bot.db.execute('CREATE TABLE IF NOT EXISTS f_users (userid integer, name text, guildid integer, coins double, trophyoid text, trophyrodlvl int, hexcolor text, reviewmsgid integer)')
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_bans (userid int, bannedwhen blob, reason text)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS collections (userid int, oid blob)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_rods (level int, name text, cost int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_stats (totalfished int, totalcoins int, totalrodsbought)")
    
    cur = await bot.db.execute('SELECT * FROM f_prefixes')
    bot.prefixes = {guild_id: prefix for guild_id, prefix in (await cur.fetchall())}
bot.loop.create_task(startup(bot))

############################################################################################################################################################################################
    
@bot.event
async def on_ready():
    print('-------------------------------------------------------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-------------------------------------------------------')
    print(myname, bot.version,"is connected and running")
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
