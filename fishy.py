# pylint: disable=wrong-import-order, missing-function-docstring, invalid-name, broad-except, too-many-branches, too-many-statements, too-many-locals, 
from cogs.owner import OWNER_ID
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
        fish_range = rod_level * 3.163265306122449
        fish_range = round(fish_range, 1)
        thing = random.choices([True,False], weights=(0.1,0.9),k=1)
        if thing:
            cur = await self.bot.db.execute("SELECT * FROM fishes WHERE fishlength <= ? AND fishlength >= ? ORDER BY RANDOM();",(fish_range, math.floor(rod_level),))
            data = await cur.fetchone()
            if data is None:
                cur = await self.bot.db.execute("SELECT * FROM fishes WHERE fishlength <= ? ORDER BY RANDOM();",(fish_range,))
                data = await cur.fetchone()
            else: pass
        else:
            cur = await self.bot.db.execute("SELECT * FROM fishes WHERE fishlength <= ? ORDER BY RANDOM();",(fish_range,))
            data = await cur.fetchone()
        return dbc.fish(self.bot, data)

class FpyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
    async def get_context(self, message, *, cls=FishyContext):
        return await super().get_context(message, cls=cls)
    
    async def prompt(self, authorid, message: discord.Message, *, timeout=60.0, delete_after=True, author_id=None):
        """Credit to Rapptz
        https://github.com/Rapptz/RoboDanny/blob/715a5cf8545b94d61823f62db484be4fac1c95b1/cogs/utils/context.py#L93"""
        confirm = None

        for emoji in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
            await message.add_reaction(emoji)

        def check(payload):
            nonlocal confirm
            if payload.message_id != message.id or payload.user_id != authorid:
                return False
            codepoint = str(payload.emoji)
            if codepoint == '\N{WHITE HEAVY CHECK MARK}':
                confirm = True
                return True
            elif codepoint == '\N{CROSS MARK}':
                confirm = False
                return True
            return False

        try:
            await bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None

        try:
            if delete_after:
                await message.delete()
        finally:
            return confirm
    
    async def usercheck(self, user): # this function checks if the user exists in the DB
        if isinstance(user, (discord.User, discord.Member)):
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
        
    async def get_player(self, user):
        if isinstance(user, int):
            #looks like an user ID, lets convert
            userobj = self.get_user(user)
            if userobj is None:
                userobj = await self.fetch_user(user)
            if userobj is None:
                return None
        elif isinstance(user, (discord.User, discord.Member)):
            userobj = user
        else:
            raise TypeError(f"get_player takes either int or discord.User or discord.Member, not {type(user)}")
        
        c = await self.db.execute("SELECT * FROM f_users WHERE userid = ?",(userobj.id,))
        data = await c.fetchone()
        if data is None: return data
        return dbc.player(self, data, userobj)
    
    async def get_fish(self, oid):
        """Gets a fish by OID, returns None if theres nothing matching."""
        c = await self.db.execute("SELECT * FROM fishes WHERE oid = ?",(oid,))
        data = await c.fetchone()
        if data is None:
            return data
        return dbc.fish(self, data)
    
    async def is_verified(self, user):
        if isinstance(user, int):
            #looks like an user ID, lets convert
            userobj = self.get_user(user)
            if userobj is None:
                userobj = await self.fetch_user(user)
            if userobj is None:
                return None
        if user is None:
            return
        c = await self.db.execute("SELECT * FROM f_verified WHERE userid = ?", (user.id,))
        data = await c.fetchone()
        if data is not None:
            return True
        else:
            return False
    
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
defaultprefix = '!'
async def get_prefix(bot, message):
    if message.guild is None:
        return ""
    return bot.prefixes.get(message.guild.id, defaultprefix)
bot = FpyBot(command_prefix=get_prefix,intents=discord.Intents(reactions=True, messages=True, members=True, guilds=True))
initial_extensions = ['jishaku','cogs.jsk_override', 'cogs.owner', 'cogs.shop','cogs.fst', 'cogs.meta', 'cogs.events', 'cogs.game', 'cogs.newhelp', 'cogs.playermeta']

#BOT#VARS#####################################################################################################
bot.ownerID = 267410788996743168
bot.launch_time = datetime.utcnow()
bot.version = '1.1.2'
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
bot.autofishers = []
bot.channel_blacklist = []
bot.uses = {}
bot.rodsbought = 0
bot.last_backup_message = ""
async def startup(bot):
    bot.db = await aiosqlite.connect('fpy.db')
    await bot.db.execute('CREATE TABLE IF NOT EXISTS f_prefixes (guildid int, prefix text)')
    await bot.db.execute('CREATE TABLE IF NOT EXISTS f_users (userid integer, name text, guildid integer, rodlevel int, coins double, trophyoid text, trophyrodlvl int, hexcolor text, reviewmsgid integer, totalcaught int, autofishingnotif int, netlevel int)')
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_bans (userid int, bannedwhen blob, reason text)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_collections (userid int, oid blob)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_rods (level int, name text, cost int)") # Not for users
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_nets (level int, name text, cost int, mins double)") # Also not for users
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_stats (totalfished int, totalcoinsearned int, totalrodsbought int, totalautofished int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_blacklist (channelid int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS f_verified (userid int)")
    
    cur = await bot.db.execute('SELECT * FROM f_prefixes')
    dbprefixes = await cur.fetchall()
    bot.prefixes = {guild_id: prefix for guild_id, prefix in dbprefixes}
    await bot.db.commit()
bot.loop.create_task(startup(bot))

############################################################################################################################################################################################

@bot.check
async def blacklist_check(ctx: FishyContext):
    if ctx.channel.id in bot.channel_blacklist and ctx.author.id != OWNER_ID:
        raise botchecks.BlacklistedChannel()
    else: return True

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
