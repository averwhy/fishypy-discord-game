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
from .utils import player, fish, botchecks

class playermeta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.check(botchecks.ban_check)
    @commands.command(aliases=["prof","me"], description="player profile, rod level, collection")
    async def profile(self, ctx, user: discord.User = None): # profile command
        dbuser = player.player()
        tfish = fish()
        if user is None:
            user = ctx.author
        checkuser = await self.bot.usercheck(user.id)
        if checkuser is False:
            await ctx.send_in_codeblock(f"I was unable to retrieve your profile. Have you done {ctx.prefix}start yet?")
            return
        # rewrite
        await ctx.send('.')
        
    @commands.check(botchecks.ban_check)
    @commands.guild_only()
    @commands.command(description="adds you to the database")
    async def start(self, ctx): # adds users to DB so they can fish
        async with ctx.channel.typing():
            result = await player.create(self.bot, userobject=ctx.author)
            await asyncio.sleep(0.5)
            if result:
                return await ctx.send_in_codeblock(f"youre added! use {ctx.prefix} to start fishing.", language='css')
            else:
                #user exists
                await ctx.send_in_codeblock(f"you're already in the database, {ctx.author.name}")
      
    @commands.check(botchecks.ban_check)
    @commands.cooldown(1,5,BucketType.user)
    @commands.command(description="views your or someone elses trophy")
    async def trophy(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        authorid = user.id
        checkuser = await self.bot.usercheck(authorid)
        if checkuser is not False:
            data1 = await self.bot.grab_db_user(authorid)
            dbuser = player()
            data = await dbuser.get_trophy(data1)
            if data is None:
                embed = discord.Embed(title=f"You dont have a Trophy!",description="Try Fishing!")
            else:
                embed = discord.Embed(title=f"{user.name}'s Trophy",url=data[1],colour=discord.Colour(0x00cc00))
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
                f = fish()
                raritycalc = f.calculate_rarity(data[4])
                dbPos = data[3]
                embed.add_field(name=tvalue,value=f"{raritycalc}({data[4]} cm), #{dbPos} in database")
            await ctx.send(embed=embed)
                
    @commands.check(botchecks.ban_check)
    @commands.cooldown(1,300,BucketType.user)
    @commands.command(description="leave a review for fishy.py :)")
    async def review(self, ctx, *, reviewtext): # review command. Sends a message to fishypy guild and saves that message ID in db. If user has sent a review it checks for that and edits it if it exists.
        authorid = ctx.message.author.id
        authorname = ctx.message.author.name
        checkuser = await self.bot.usercheck(authorid)
        if checkuser is not False:
            data = await self.bot.grab_db_user(id=authorid)
            user = player.player(data)
            askmessage = await ctx.send("`Are you sure you would like to submit your review? `")
            await askmessage.add_reaction(emoji="\U00002705") # white check mark
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
            except asyncio.TimeoutError:
                try:
                    await askmessage.clear()
                except: #no reaction perms
                    pass 
                await askmessage.edit(content="`Prompt timed out. Try again`")
            else:
                m = await user.update_review(userobject=ctx.author,reviewtext=reviewtext)
                # and then
                await askmessage.clear_reactions()
                await askmessage.edit(content=m)   
        else:
            await ctx.send(f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
            
def setup(bot):
    bot.add_cog(playermeta(bot))