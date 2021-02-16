# pylint: disable=wrong-import-order, missing-function-docstring, invalid-name, broad-except, too-many-branches, too-many-statements, too-many-locals, 
import platform
import traceback
import asyncio
import time, random
import os, sys
import aiosqlite
import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
from .utils import botchecks
from .utils.dbc import player, fish

class playermeta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.check(botchecks.ban_check)
    @commands.command(aliases=["prof","me"], description="player profile, rod level, collection")
    async def profile(self, ctx, user: discord.User = None): # profile command
        """shows you your player profile (coins, collection, total caught, trophy, etc). \nyou can also view other users profiles, for example !profile @Fishy.py"""
        if user is None:
            user = ctx.author
        playeruser = await self.bot.get_player(user.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        collection_length = await self.bot.db.execute("SELECT COUNT(*) FROM f_collections WHERE userid = ?",(user.id,))
        embed = discord.Embed(title=user.name)
        embed.add_field(name="__Coins__", value=round(playeruser.coins,2))
        embed.add_field(name="__Collection__", value=(await playeruser.get_collection()))
        embed.add_field(name="__Total Caught__", value=f"{playeruser.total_caught} fish")
        playerrod = await playeruser.get_rod()
        embed.add_field(name="__Rod__", value=f"**{playerrod.name}** (Max length {playerrod.max_length}cm)")
        embed.set_thumbnail(url=user.avatar_url)
        if playeruser.trophy_oid not in [None, 'none']:
            playertrophy = await self.bot.get_fish(playeruser.trophy_oid)
            embed.set_image(url=playertrophy.image_url)
            embed.color = (await fish.fancy_rarity(playertrophy.rarity))[1]
            embed.add_field(name=f"__Trophy: {playertrophy.name}__", value=f"**Length:** {playertrophy.original_length} cm; **worth:** {playertrophy.coins(playeruser.trophy_rod_level)} coins", inline=False)
        else:
            embed.add_field(name="__Trophy__", value="None, try fishing!")
        await ctx.reply(embed=embed)
        
    @commands.check(botchecks.ban_check)
    @commands.guild_only()
    @commands.command(description="adds you to the database")
    async def start(self, ctx): # adds users to DB so they can fish
        """registers you to the database.\nthis command exists so people know when they're giving their data to the bot.\nif you want your data deleted, please join the support server by doing !support"""
        result = await player.create(self.bot, ctx.author)
        reactions = ['✅', '<:yesfish:810187479466115102>', '<a:snod:798165766888488991>']
        if result:
            selected_reaction = (random.choices(reactions, weights=[0.8, 0.1, 0.1], k=1))[0]
            return await ctx.message.add_reaction(selected_reaction)
        await ctx.reply_in_codeblock("you're already in the database")
      
    @commands.check(botchecks.ban_check)
    @commands.cooldown(1,5,BucketType.user)
    @commands.command(description="views your or someone elses trophy")
    async def trophy(self, ctx, user: discord.User = None):
        """shows your trophy (longest fish caught)\ncan also view another users trophy, for example: !trophy @Fishy.py"""
        if user is None:
            user = ctx.author

            
def setup(bot):
    bot.add_cog(playermeta(bot))