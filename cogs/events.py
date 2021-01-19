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
from .utils import botchecks

class events(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.commandsRun += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): # this is an event that runs when there is an error
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):   
            return
        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown): 
            emote = str(discord.PartialEmoji(name="ppOverheat", id=772189476704616498, animated=True))
            s = round(error.retry_after,2)
            if s > 3600: # over 1 hour
                s /= 3600
                s = round(s,1)
                s = f"{s} hour(s)"
            elif s > 60: # over 1 minute
                s /= 60
                s = round(s,2)
                s = f"{s} minute(s)"
            else: #below 1 min
                s = f"{s} seconds"
            msgtodelete = await ctx.send(f"`ERROR: Youre on cooldown for {s}!` {emote}")
            await asyncio.sleep(self.bot.secondstoReact)
            await msgtodelete.delete()
            return
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            msgtodelete = await ctx.send("`ERROR: Missing permissions.`")
            await asyncio.sleep(10)
            await msgtodelete.delete()
        elif isinstance(error, botchecks.BanCheckError):
            await ctx.send(f"`ERROR: You are banned! Please join the Fishy.py support server to appeal. ({bot.defaultprefix}support)`")
            return
        elif isinstance(error, botchecks.IsNotInGuild):
            await ctx.send(f"`ERROR: Sorry, you can only run this command in a guild. Right now you are DM'ing me!`")
            return
        else:
            self.bot.commandsFailed += 1
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await ctx.send_in_codeblock(f"Internal Error\n- {error}",language='diff')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logchannel = self.bot.get_channel(761683999772377128)
        if logchannel is None:
            logchannel = await self.bot.fetch_channel(761683999772377128)
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
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logchannel = self.bot.get_channel(761683999772377128)
        if logchannel is None:
            logchannel = await self.bot.fetch_channel(761683999772377128)
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
        
        
def setup(bot):
    bot.add_cog(events(bot))