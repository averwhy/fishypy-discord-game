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

from .utils.dbc import player, fish
from .utils import botchecks

class shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True, name='shop', description='shows you the prices of upgrades for rods')
    async def _shop(self, ctx):
        """the main shop command."""
        await ctx.send_in_codeblock(f"usage: {ctx.prefix}shop [rods]")

    @_shop.command(aliases=["rod","r"])
    async def rods(self, ctx):
        """shows you your current rod, and the upcoming rods you can buy."""
        playeruser = await self.bot.get_player(ctx.author.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        lvl = playeruser.rod_level
        cur = await self.bot.db.execute("SELECT * FROM f_rods WHERE level = ?",(playeruser.rod_level,))
        data = await cur.fetchone()
        table = f"#________SHOP RODS________#"
        for r in range(6):
            step = r + lvl
            if step == lvl:
                cur = await self.bot.db.execute("SELECT * FROM f_rods WHERE level = ?",(step,))
                data = await cur.fetchone()
                table = table + f"\n[{data[1]}][{data[2]} coins] *current rod*"
            else:
                cur = await self.bot.db.execute("SELECT * FROM f_rods WHERE level = ?",(step,))
                data = await cur.fetchone()
                table = table + f"\n[{data[1]}][{data[2]} coins]"
        
        table = table + f"\n(and more...)({playeruser.coins} coins)"
        await ctx.reply_in_codeblock(table, language='md')
    
    @commands.group(invoke_without_command=True, aliases=["u"])
    async def upgrade(self, ctx):
        """buys something."""
        await ctx.send_in_codeblock(f"please specify {ctx.prefix}upgrade rod")
        
    @upgrade.command(name='rod')
    async def _rod(self, ctx):
        """buys the next avaliable rod automatically, if you have enough coins."""
        playeruser = await self.bot.get_player(ctx.author.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        cur = await self.bot.db.execute("SELECT * FROM f_rods WHERE level = ?",((playeruser.rod_level + 1),))
        data = await cur.fetchone()
        if data is None:
            return await ctx.reply_in_codeblock('you have the max rod level!', language='css')
        
        if playeruser.coins < data[2]:
            return await ctx.reply_in_codeblock(f'you cannot afford a rod upgrade, you need {data[2] - playeruser.coins} more coins')
        
        await self.bot.db.execute("UPDATE f_users SET rodlevel = (rodlevel + 1) WHERE userid = ?",(ctx.author.id,))
        await self.bot.db.commit()
        await ctx.reply_in_codeblock(f"success! new rod: {data[1]}")
        
            
def setup(bot):
    bot.add_cog(shop(bot))
        