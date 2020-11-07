import discord
import aiohttp
import asyncio
import time
import random, math
import json
import re, os, sys
import aiosqlite
import traceback
import jishaku
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
wordlist = ["yoinked","yeeted","throwned","chucked","lobbed","propelled","bit the dust","tossed","is now sleeping with the fishes","launched"] # because funny

class IsntSupportServer(CheckFailure):
    pass

async def is_support_server(ctx):
    if ctx.guild.id == 734581170452430888:
        return True
    else:
        raise IsntSupportServer()

class FishyServerTools(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.issue = re.compile(r'##(?P<number>[0-9]+)') # also thanks rapptz
    
    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
        if isinstance(error, IsntSupportServer):
            pass # so nothing happens
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            
    @commands.Cog.listener()
    async def on_message(self,message):
        #credit to Rapptz for this:
        m = self.issue.search(message.content)
        if m is not None:
            url = 'https://github.com/averwhy/fishy-discord-game/issues/'
            await message.channel.send(url + m.group('number'))
    
    @commands.check(is_support_server)
    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=["b"])
    async def ban(self,ctx,member: discord.Member = None,*,reason = None):
        global wordlist
        askmessage = await ctx.send(f"`Are you sure you want to ban {member.name} from the support server?`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Timed out.`")
        else:
            await member.ban(reason=reason)
            await ctx.send(f"`{str(member)} {random.choice(wordlist)}!`")
    
    @commands.check(is_support_server)
    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=["ub"])
    async def unban(self,ctx,member: discord.Member = None,*,reason = None):
        await member.unban(reason=reason)
        await ctx.send(f"`{str(member)} unbanned!`")
    
    @commands.check(is_support_server)
    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=["k"])
    async def kick(self,ctx,member: discord.Member = None,*,reason):
        global wordlist
        askmessage = await ctx.send(f"`Are you sure you want to kick {member.name} from the support server?`")
        await askmessage.add_reaction(emoji="\U00002705") # white check mark
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Timed out.`")
        else:
            await member.kick(reason=reason)
            await ctx.send(f"`{str(member)} {random.choice(wordlist)}!`")
            
    @commands.check(is_support_server)
    @commands.has_role(758408309383757894)
    @commands.command(aliases=["l","lc"])
    async def lock(self, ctx, chnnel: discord.TextChannel = None):
        try:
            everyone = ctx.guild.default_role
            if ctx.channel.overwrites_for(ctx.channel).send_messages in [None,True]:
                if chnnel is None:
                    currentperms = ctx.channel.overwrites_for(everyone)
                    currentperms.send_messages = False
                    await ctx.channel.set_permissions(everyone, overwrite=currentperms,reason=(f"Channel lock by {str(ctx.author)}"))
                    await ctx.channel.send(f"🔒 `#{ctx.channel.name} was locked`")
                elif chnnel is not None:
                    newperms = discord.PermissionOverwrite()
                    newperms.send_messages = False
                    await chnnel.set_permissions(everyone, overwrite=newperms,reason=(f"Channel lock by {str(ctx.author)}"))
                    await ctx.channel.send(f"🔒 `#{chnnel.name} was locked`")
            else:
                if chnnel is None:
                    currentperms = ctx.channel.overwrites_for(everyone)
                    currentperms.send_messages = None
                    await ctx.channel.set_permissions(everyone, overwrite=currentperms,reason=(f"Channel unlock by {str(ctx.author)}"))
                    await ctx.channel.send(f"🔓 `#{ctx.channel.name} was unlocked`")
                elif chnnel is not None:
                    newperms = discord.PermissionOverwrite()
                    newperms.send_messages = None
                    await chnnel.set_permissions(everyone, overwrite=newperms,reason=(f"Channel unlock by {str(ctx.author)}"))
                    await ctx.channel.send(f"🔓 `#{chnnel.name} was unlocked`")
        except Exception as e:
            await ctx.send(f"`Something went wrong:` ```\n{e}\n```")

    @commands.check(is_support_server)
    @commands.command(aliases=["sl"])
    @commands.has_permissions(manage_guild=True)
    async def serverlock(self, ctx):
        try:
            await ctx.send("`Locking... Do note, it locks at an interval of 1 channel/0.5s`")
            newperms = discord.PermissionOverwrite()
            for c in ctx.guild.channels:
                newperms.send_messages = False
                await c.set_permissions(overwrite=newperms,reason=f"Server lock by {str(ctx.author)}")
                await asyncio.sleep(0.5)
        except Exception as e:
            await ctx.send(f"`Something went wrong:` ```\n{e}\n```")
            
def setup(bot):
    bot.add_cog(FishyServerTools(bot))