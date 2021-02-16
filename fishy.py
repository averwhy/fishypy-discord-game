# pylint: disable=wrong-import-order, missing-function-docstring, invalid-name, broad-except, too-many-branches, too-many-statements, too-many-locals, 
import platform
import traceback
import asyncio
import time
import os, sys
import aiosqlite
import discord
import math, random
import typing
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check

from cogs.utils import dbc, botchecks
#BOT##########################################################################################################
class FishyContext(commands.Context):
    #self = ctx
    async def send_in_codeblock(self, content, *, language: str = None, embed: discord.Embed = None, delete_after: float = None):
        if language is None:
            lang = ''
        else:
            lang = language
        return await self.send(f"```{lang}\n{content}```", embed=embed, delete_after=delete_after)

    async def reply_in_codeblock(self, content, *, language: str = None, embed: discord.Embed = None, delete_after: float = None):
        if language is None:
            lang = ''
        else:
            lang = language
        return await self.reply(f"```{lang}\n{content}```", embed=embed, delete_after=delete_after)
        
    async def random_fish(self, rod_level):
        fish_range = (0.9) * math.floor(rod_level)
        c = await self.bot.db.execute("SELECT COUNT(*) FROM fishes WHERE fishlength <= ?",(fish_range,))
        fish_in_range = (await c.fetchone())[0]
        fish_range = math.floor(random.uniform(0,1) * fish_in_range)
        if fish_range == 0: fish_range = 1 # to prevent 0's
        cur = await self.bot.db.execute("SELECT * FROM fishes WHERE fishlength <= ? AND fishlength >= ? ORDER BY RANDOM();",(fish_range, math.floor(rod_level),))
        data = await cur.fetchone()
        return dbc.fish(self.bot, data)

class FpyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
    async def get_context(self, message, *, cls=FishyContext):
        return await super().get_context(message, cls=cls)
    
    async def usercheck(self, user): # this function checks if the user exists in the DB
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = user.id
        elif isinstance(user, int):
            pass
        else:
            raise TypeError('Paramater must be int or discord.User')
        cur = await self.db.execute("SELECT * FROM f_users WHERE userid = ?",(user,))
        data = await cur.fetchone()
        await bot.db.commit()
        if data is None:
            return False #Not In database
        return True #in database
        
    async def get_player(self, pid):
        c = await self.db.execute("SELECT * FROM f_users WHERE userid = ?",(pid,))
        data = await c.fetchone()
        if data is None: return data
        return dbc.player(self, data)
    
    async def get_fish(self, oid):
        """Gets a fish by OID, returns None if theres nothing matching."""
        c = await self.db.execute("SELECT * FROM fishes WHERE oid = ?",(oid,))
        data = await c.fetchone()
        if data is None:
            return data
        return dbc.fish(self, data)
    
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
bot = FpyBot(command_prefix=get_prefix,intents=discord.Intents(reactions = True, messages = True, guilds = True, members = True))
bot.remove_command('help')
initial_extensions = ['jishaku','cogs.jsk_override', 'cogs.owner', 'cogs.funnypicture', 'cogs.shop','cogs.fst', 'cogs.meta', 'cogs.events', 'cogs.game', 'cogs.newhelp', 'cogs.playermeta']

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
bot.coinsEarnedInSession = 0
bot.commandsRun = 0
bot.commandsFailed = 0
bot.defaultprefix = defaultprefix
bot.coin_multiplier = 1.0
bot.seconds_to_react = 5
bot.fishers = []
bot.uses = {}
bot.rodsbought = 0
async def startup(bot):
    bot.db = await aiosqlite.connect('fpy.db')
    await bot.db.execute('CREATE TABLE IF NOT EXISTS f_prefixes (guildid int, prefix text)')
    await bot.db.execute('CREATE TABLE IF NOT EXISTS f_users (userid integer, name text, guildid integer, rodlevel int, coins double, trophyoid text, trophyrodlvl int, hexcolor text, reviewmsgid integer, totalcaught int)')
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_bans (userid int, bannedwhen blob, reason text)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_collections (userid int, oid blob)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_rods (level int, name text, cost int)") # Not for users
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_stats (totalfished int, totalcoinsearned int, totalrodsbought int)")
    
    cur = await bot.db.execute('SELECT * FROM f_prefixes')
    dbprefixes = await cur.fetchall()
    bot.prefixes = {guild_id: prefix for guild_id, prefix in dbprefixes}
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
