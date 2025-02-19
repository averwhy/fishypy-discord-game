from cogs.owner import OWNER_ID
import traceback
import asyncio
import os, sys
import aiosqlite
import discord
import random
from discord.ext import commands
import humanize
import typing
import objgraph
import io
from contextlib import redirect_stdout
from cogs.utils import dbc, botchecks


# BOT##########################################################################################################
class FishyContext(commands.Context):
    # self = ctx
    async def send_in_codeblock(
        self,
        content,
        *,
        language: str = None,
        embed: discord.Embed = None,
        delete_after: float = None,
    ):
        if language is None:
            lang = ""
        else:
            lang = language
        return await self.send(
            f"```{lang}\n{content}```", embed=embed, delete_after=delete_after
        )

    async def reply_in_codeblock(
        self,
        content,
        *,
        language: str = None,
        embed: discord.Embed = None,
        delete_after: float = None,
    ):
        if language is None:
            lang = ""
        else:
            lang = language
        return await self.reply(
            f"```{lang}\n{content}```", embed=embed, delete_after=delete_after
        )

    async def fish(self, rod_level):
        max_length = round(rod_level * 3.163265306122449, 2)

        cur = await self.bot.db.execute(
            "SELECT oid, rarity, fishlength FROM fishes WHERE fishlength <= ?",
            (max_length,),
        )
        fish_list = await cur.fetchall()
        if not fish_list:
            return None

        weighted_rarities = []
        total_weighted_rarity = 0.0
        for fish in fish_list:
            rarity = float(fish[1])
            fishlength = float(fish[2])

            weighted_rarity = (
                rarity * (1 + (rod_level * bot.RARITY_SCALING_FACTOR / 100))
            ) + (
                fishlength
                * (1 + (rod_level * bot.LENGTH_SCALING_FACTOR / 100))
                / max_length
            )
            weighted_rarities.append(weighted_rarity)
            total_weighted_rarity += weighted_rarity

        probabilities = [w / total_weighted_rarity for w in weighted_rarities]
        random_value = random.random()
        cumulative_probability = 0.0
        for i, probability in enumerate(probabilities):
            cumulative_probability += probability
            if random_value < cumulative_probability:
                # Fetch the complete fish data using the oid
                cur = await self.bot.db.execute(
                    "SELECT * FROM fishes WHERE oid = ?", (fish_list[i][0],)
                )
                fish_data = await cur.fetchone()
                return dbc.Fish(self.bot, fish_data)

        # Fallback
        cur = await self.bot.db.execute(
            "SELECT * FROM fishes WHERE oid = ?", (fish_list[-1][0],)
        )
        fish_data = await cur.fetchone()
        return dbc.Fish(self.bot, fish_data)


class FpyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        self.db = await aiosqlite.connect("fpy.db")
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_prefixes (guildid int, prefix text)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_users (userid integer, name text, guildid integer, rodlevel int, coins double, trophyoid text, trophyrodlvl int, hexcolor text, reviewmsgid integer, totalcaught int, autofishingnotif int, netlevel int, highestrod int)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_bans (userid int, bannedwhen blob, reason text)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_collections (userid int, oid blob)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_rods (level int, name text, cost int)"
        )  # Not for users
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_nets (level int, name text, cost int, mins double)"
        )  # Also not for users
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS f_stats (totalfished int, totalcoinsearned int, totalrodsbought int, totalautofished int)"
        )
        await self.db.execute("CREATE TABLE IF NOT EXISTS f_blacklist (channelid int)")
        await self.db.execute("CREATE TABLE IF NOT EXISTS f_verified (userid int)")

        cur = await self.db.execute("SELECT * FROM f_prefixes")
        dbprefixes = await cur.fetchall()
        self.prefixes = {guild_id: prefix for guild_id, prefix in dbprefixes}
        await self.db.commit()

        success = failed = 0
        for cog in self.initial_extensions:
            try:
                await self.load_extension(f"{cog}")
                success += 1
            except Exception as e:
                print(f"failed to load {cog}, error:\n", file=sys.stderr)
                failed += 1
                traceback.print_exc()
            finally:
                continue
        print(f"loaded {success} cogs successfully, with {failed} failures.")

    async def get_context(self, message, *, cls=FishyContext):
        return await super().get_context(message, cls=cls)

    async def prompt(
        self,
        authorid,
        message: discord.Message,
        *,
        timeout=60.0,
        delete_after=True,
        author_id=None,
    ):
        """Credit to Rapptz
        https://github.com/Rapptz/RoboDanny/blob/715a5cf8545b94d61823f62db484be4fac1c95b1/cogs/utils/context.py#L93
        """
        confirm = None

        for emoji in ("\N{WHITE HEAVY CHECK MARK}", "\N{CROSS MARK}"):
            await message.add_reaction(emoji)

        def check(payload):
            nonlocal confirm
            if payload.message_id != message.id or payload.user_id != authorid:
                return False
            codepoint = str(payload.emoji)
            if codepoint == "\N{WHITE HEAVY CHECK MARK}":
                confirm = True
                return True
            elif codepoint == "\N{CROSS MARK}":
                confirm = False
                return True
            return False

        try:
            await bot.wait_for("raw_reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None

        try:
            if delete_after:
                await message.delete()
        finally:
            return confirm

    async def usercheck(
        self, user
    ) -> bool:  # this function checks if the user exists in the DB
        if isinstance(user, (discord.User, discord.Member)):
            user = user.id
        elif isinstance(user, int):
            pass
        else:
            raise TypeError("Paramater must be int or discord.User")
        cur = await self.db.execute("SELECT * FROM f_users WHERE userid = ?", (user,))
        data = await cur.fetchone()
        await bot.db.commit()
        if data is None:
            return False  # Not In database
        return True  # in database

    async def get_player(self, user) -> typing.Union[dbc.Player, None]:
        if isinstance(user, int):
            # looks like an user ID, lets convert
            userobj = self.get_user(user)
            if userobj is None:
                userobj = await self.fetch_user(user)
            if userobj is None:
                return None
        elif isinstance(user, (discord.User, discord.Member)):
            userobj = user
        else:
            raise TypeError(
                f"get_player takes either int, discord.User or discord.Member, not {type(user)}"
            )

        c = await self.db.execute(
            "SELECT * FROM f_users WHERE userid = ?", (userobj.id,)
        )
        data = await c.fetchone()
        if data is None:
            return data
        return dbc.Player(self, data, userobj)

    async def get_fish(self, oid) -> typing.Union[dbc.Fish, None]:
        """Gets a Fish by OID, returns None if theres nothing matching."""
        c = await self.db.execute("SELECT * FROM fishes WHERE oid = ?", (oid,))
        data = await c.fetchone()
        if data is None:
            return data
        return dbc.Fish(self, data)

    async def is_verified(self, user) -> typing.Union[bool, None]:
        if isinstance(user, int):
            # looks like an user ID, lets convert
            userobj = self.get_user(user)
            if userobj is None:
                userobj = await self.fetch_user(user)
            if userobj is None:
                return None
        if user is None:
            return
        c = await self.db.execute(
            "SELECT * FROM f_verified WHERE userid = ?", (user.id,)
        )
        data = await c.fetchone()
        return bool(data is not None)

    async def rodUpgradebar(self, rodlvl):
        return f"{'#' * (decimal := round(rodlvl % 1 * 15))}{'_' * (15 - decimal)}"


os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
with open(os.environ["SECRETS"], "r") as t:
    TOKEN = t.readline()
userid = "695328763960885269"
myname = "Fishy.py"
sinvite = "https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot"
defaultprefix = "!"


async def get_prefix(bot, message) -> str:
    if message.guild is None:
        return ""
    return bot.prefixes.get(message.guild.id, defaultprefix)


bot = FpyBot(
    command_prefix=get_prefix,
    chunk_guilds_on_startup=False,
    intents=discord.Intents(
        reactions=True, messages=True, members=True, guilds=True, message_content=True
    ),
)

# BOT#VARS#####################################################################################################
bot.ownerID = 267410788996743168
bot.launch_time = discord.utils.utcnow()
bot.version = "2.1.2"
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
bot.RARITY_SCALING_FACTOR = 1.3
bot.LENGTH_SCALING_FACTOR = 2
bot.initial_extensions = [
    "jishaku",
    "cogs.jsk_override",
    "cogs.owner",
    "cogs.shops",
    "cogs.fst",
    "cogs.meta",
    "cogs.events",
    "cogs.game",
    "cogs.newhelp",
    "cogs.playermeta",
]


async def startup():
    async with bot:
        await bot.start(TOKEN)


############################################################################################################################################################################################
from discord.ext.commands.errors import CommandNotFound, CommandOnCooldown, NotOwner


@bot.event
async def on_command_error(
    ctx, error
):  # this is an event that runs when there is an error
    if isinstance(error, commands.errors.CommandNotFound):
        return
    elif isinstance(error, CommandOnCooldown):
        s = round(error.retry_after, 2)
        s = humanize.naturaldelta(s)
        msgtodelete = await ctx.send_in_codeblock(f"error; cooldown for {s}")
        await asyncio.sleep(bot.secondstoReact)
        await msgtodelete.delete()
        return
    elif isinstance(error, NotOwner):
        msgtodelete = await ctx.send_in_codeblock("error; missing permissions")
        await asyncio.sleep(15)
        await msgtodelete.delete()
    elif isinstance(error, botchecks.BanCheckError):
        await ctx.send_in_codeblock(
            f"error; you're banned! please join the Fishy.py support server to appeal ({ctx.prefix}support)"
        )
        return
    elif isinstance(error, botchecks.IsNotInGuild):
        await ctx.send_in_codeblock(
            f"error; sorry, you can only run this command in a guild. right now you are DM'ing me!"
        )
        return
    elif isinstance(error, botchecks.BlacklistedChannel):
        return
    elif isinstance(error, discord.errors.Forbidden):
        try:
            await ctx.send_in_codeblock(
                "error; i'm missing some permissions. please make sure i have embed permissions, manage messages, and use external emojis."
            )
        except Exception:
            # RIP
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
    else:
        bot.commandsFailed += 1
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )
        await ctx.send_in_codeblock(f"Internal Error\n- {error}", language="diff")


@bot.check
async def blacklist_check(ctx: FishyContext):
    if ctx.channel.id in bot.channel_blacklist and ctx.author.id != OWNER_ID:
        raise botchecks.BlacklistedChannel()
    else:
        return True


@bot.command(hidden=True)
async def leakcheck(ctx):
    """Developer command to check results of objgraph"""
    async with ctx.channel.typing():
        with io.StringIO() as buf, redirect_stdout(buf):
            objgraph.show_most_common_types(limit=30)
            output = buf.getvalue()
    return await ctx.send(f"```py\n{output}```")


@bot.event
async def on_ready():
    print("-------------------------------------------------------")
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    print("")
    print(bot.user.name, bot.version, "is connected and running")
    print(f"Time since start: {humanize.precisedelta(bot.launch_time.replace(tzinfo=None))}")
    print("-------------------------------------------------------")


if __name__ == "__main__":
    discord.utils.setup_logging(root=True)
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    asyncio.run(startup())
