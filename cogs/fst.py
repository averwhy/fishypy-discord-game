import discord
import asyncio
import random
import re, sys
import traceback
from discord.ext import commands
from discord.ext.commands import CheckFailure

wordlist = [
    "yoinked",
    "yeeted",
    "throwned",
    "chucked",
    "lobbed",
    "propelled",
    "bit the dust",
    "tossed",
    "is now sleeping with the fishes",
    "launched",
]  # because funny
FPY_CONTRIBUTOR_ROLE = 758428311038066718
FPY_MOD_ROLE = 758408309383757894
FPY_BETA_ROLE = 752227026647122031
CATEGORIES_TO_IGNORE = [
    742840533256241254,
    None,
]  # If its none, its either the start, welcome, dpy updates, fpy updates, or news channel. If it matches that ID, its the fishy.py dev category


class IsntSupportServer(CheckFailure):
    pass


async def is_support_server(ctx):
    if ctx.guild.id == 734581170452430888:
        return True
    raise IsntSupportServer()


class fst(commands.Cog, command_attrs=dict(hidden=True)):
    """fst = Fishy Server Tools. These are commands for the support server."""

    def __init__(self, bot):
        self.bot = bot
        self.issue = re.compile(r"##(?P<number>[0-9]+)")  # thanks rapptz :)

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
        if isinstance(error, IsntSupportServer):
            pass  # so nothing happens
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        # credit to Rapptz for this:
        m = self.issue.search(message.content)
        if m is not None:
            if message.guild.id == 734581170452430888:
                url = "https://github.com/averwhy/fishy-discord-game/issues/"
                await message.channel.send(url + m.group("number"))

    @commands.check(is_support_server)
    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=["b"])
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        global wordlist
        try:
            await member.ban(reason=reason)
            await ctx.message.add_reaction(emoji="\U00002705")
            await ctx.send(f"`{str(member)} {random.choice(wordlist)}!`")
        except Exception as e:
            await ctx.send(f"`Something went wrong: {e}`")

    @commands.check(is_support_server)
    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=["ub"])
    async def unban(self, ctx, member: discord.User = None, *, reason=None):
        try:
            await member.unban(reason=reason)
            await ctx.send(f"`{str(member)} unbanned!`")
        except Exception as e:
            await ctx.send(f"`I couldnt unban that user: {e}`")

    @commands.check(is_support_server)
    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=["k"])
    async def kick(self, ctx, member: discord.Member = None, *, reason):
        global wordlist
        try:
            await member.kick(reason=reason)
            await ctx.message.add_reaction(emoji="\U00002705")
            await ctx.send(f"`{str(member)} {random.choice(wordlist)}!`")
        except Exception as e:
            await ctx.send(f"`Something went wrong: {e}`")

    @commands.check(is_support_server)
    @commands.has_role(758408309383757894)
    @commands.command(aliases=["l", "lc"])
    async def lock(self, ctx, chnnel: discord.TextChannel = None):
        try:
            everyone = ctx.guild.default_role
            if chnnel is None:
                if ctx.channel.overwrites_for(everyone).send_messages in [None, True]:
                    currentperms = ctx.channel.overwrites_for(everyone)
                    currentperms.send_messages = False
                    await ctx.channel.set_permissions(
                        everyone,
                        overwrite=currentperms,
                        reason=(f"Channel lock by {str(ctx.author)}"),
                    )
                    await ctx.channel.send(f"🔒 `#{ctx.channel.name} was locked`")
                    return
                elif ctx.channel.overwrites_for(everyone).send_messages in [False]:
                    newperms = ctx.channel.overwrites_for(everyone)
                    newperms.send_messages = None
                    await ctx.channel.set_permissions(
                        everyone,
                        overwrite=newperms,
                        reason=(f"Channel lock by {str(ctx.author)}"),
                    )
                    await ctx.channel.send(f"🔒 `#{ctx.channel.name} was unlocked`")
                    return
            else:
                if chnnel.overwrites_for(everyone).send_messages in [None, True]:
                    currentperms = chnnel.overwrites_for(everyone)
                    currentperms.send_messages = False
                    await chnnel.set_permissions(
                        everyone,
                        overwrite=currentperms,
                        reason=(f"Channel unlock by {str(ctx.author)}"),
                    )
                    await chnnel.send(f"🔓 `#{chnnel.name} was unlocked`")
                    return
                elif chnnel.overwrites_for(everyone).send_messages in [False]:
                    newperms = chnnel.overwrites_for(everyone)
                    newperms.send_messages = None
                    await chnnel.set_permissions(
                        everyone,
                        overwrite=newperms,
                        reason=(f"Channel unlock by {str(ctx.author)}"),
                    )
                    await chnnel.send(f"🔓 `#{chnnel.name} was unlocked`")
                    return
        except Exception as e:
            await ctx.send(f"`Something went wrong: {e}`")

    @commands.check(is_support_server)
    @commands.command(aliases=["sl"])
    @commands.has_permissions(manage_guild=True)
    async def serverlock(self, ctx):
        try:
            everyone = ctx.guild.default_role
            await ctx.send(
                "`Locking... Do note, it locks at an interval of 1 channel/0.5s`"
            )
            currentperms = ctx.channel.overwrites_for(everyone)
            for c in ctx.guild.channels:
                if c.category_id in CATEGORIES_TO_IGNORE:
                    pass
                elif c.overwrites_for(everyone).send_messages in [False]:
                    pass
                else:
                    currentperms.send_messages = False
                    await c.set_permissions(
                        overwrite=currentperms,
                        reason=f"Server lock by {str(ctx.author)}",
                    )
                    await asyncio.sleep(0.5)
        except Exception as e:
            await ctx.send(f"`Something went wrong:` ```\n{e}\n```")

    @commands.check(is_support_server)
    @commands.command(aliases=["sul"])
    @commands.has_permissions(manage_guild=True)
    async def serverunlock(self, ctx):
        try:
            everyone = ctx.guild.default_role
            await ctx.send(
                "`Locking... Do note, it locks at an interval of 1 channel/0.5s`"
            )
            currentperms = ctx.channel.overwrites_for(everyone)
            for c in ctx.guild.channels:
                if c.category_id in CATEGORIES_TO_IGNORE:
                    pass
                elif c.overwrites_for(everyone).send_messages in [None, True]:
                    pass
                else:
                    currentperms.send_messages = None
                    await c.set_permissions(
                        overwrite=currentperms,
                        reason=f"Server lock by {str(ctx.author)}",
                    )
                    await asyncio.sleep(0.5)
        except Exception as e:
            await ctx.send(f"`Something went wrong:` ```\n{e}\n```")


async def setup(bot):
    await bot.add_cog(fst(bot))
