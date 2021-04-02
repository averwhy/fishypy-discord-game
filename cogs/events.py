# pylint: disable=wrong-import-order, missing-function-docstring, invalid-name, broad-except, too-many-branches, too-many-statements, too-many-locals, 
import platform
import traceback
import asyncio
import time
import os, sys
import aiosqlite
import aiohttp
import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
from .utils import botchecks
import humanize
SUPPORT_SERVER_ID = 734581170452430888

class events(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            cursor = await self.bot.db.execute("SELECT * FROM f_users WHERE userid = ?",(after.id,))
            data = await cursor.fetchone()
            if data is None:
                #The user doesnt exist, so do not update
                return
            else:
                #The user is in the database, lets change their name
                await self.bot.db.execute("UPDATE f_users SET name = ? WHERE userid = ?",(after.name, after.id,))
                await self.bot.db.commit()


    @commands.Cog.listener()
    async def on_message(self, message):
        ms = (message.content).strip()
        if ms in [f"{self.bot.user.mention}",f"<@!{self.bot.user.id}>",f"<@?{self.bot.user.id}>"]:
            try: prefix = self.bot.prefixes[message.guild.id]
            except KeyError: prefix = self.bot.defaultprefix
            return await message.channel.send(f"```hey, my prefix is {prefix}```")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.commandsRun += 1
        try: 
            amount = self.bot.uses[ctx.author.id]
            self.bot.uses[ctx.author.id] = amount + 1
        except KeyError: self.bot.uses[ctx.author.id] = 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): # this is an event that runs when there is an error
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):   
            return
        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown): 
            emote = str(discord.PartialEmoji(name="ppOverheat", id=772189476704616498, animated=True))
            s = round(error.retry_after,2)
            s = humanize.naturaldelta(s)
            msgtodelete = await ctx.send_in_codeblock(f"error; cooldown for {s}")
            await asyncio.sleep(self.bot.secondstoReact)
            await msgtodelete.delete()
            return
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            msgtodelete = await ctx.send_in_codeblock("error; missing permissions")
            await asyncio.sleep(10)
            await msgtodelete.delete()
        elif isinstance(error, botchecks.BanCheckError):
            await ctx.send_in_codeblock(f"error; you're banned! please join the Fishy.py support server to appeal ({ctx.prefix}support)")
            return
        elif isinstance(error, botchecks.IsNotInGuild):
            await ctx.send_in_codeblock(f"error; sorry, you can only run this command in a guild. right now you are DM'ing me!")
            return
        elif isinstance(error, botchecks.BlacklistedChannel):
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
Created:         {humanize.precisedelta(guild.created_at)}
Emoji limit:     {humanize.naturalsize(guild.emoji_limit)}```
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
Created:         {humanize.precisedelta(guild.created_at)}
Emoji limit:     {humanize.naturalsize(guild.emoji_limit)}```
                """
        await logchannel.send(msg)
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == SUPPORT_SERVER_ID:
            hook_link = os.getenv('FISHY_JOIN_HOOK')
            async with aiohttp.ClientSession() as session:
                joinhook = discord.Webhook.from_url(url=hook_link, adapter=discord.AsyncWebhookAdapter(session))
                await joinhook.send(f"{str(member)} joined!")
        else:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == SUPPORT_SERVER_ID:  
            hook_link = os.getenv('FISHY_LEAVE_HOOK')
            async with aiohttp.ClientSession() as session:
                joinhook = discord.Webhook.from_url(url=hook_link, adapter=discord.AsyncWebhookAdapter(session))
                await joinhook.send(f"{str(member)} left.")
        else:
            pass
        
        
def setup(bot):
    bot.add_cog(events(bot))