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
from .utils import dbc

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
            embed.color = (await dbc.fish.fancy_rarity(playertrophy.rarity))[1]
            embed.add_field(name=f"__Trophy: {playertrophy.name}__", value=f"**Length:** {playertrophy.original_length} cm; **worth:** {playertrophy.coins(playeruser.trophy_rod_level)} coins", inline=False)
        else:
            embed.add_field(name="__Trophy__", value="None, try fishing!")
        await ctx.reply(embed=embed)
        
    @commands.check(botchecks.ban_check)
    @commands.guild_only()
    @commands.command(description="adds you to the database")
    async def start(self, ctx): # adds users to DB so they can fish
        """registers you to the database.\nthis command exists so people know when they're giving their data to the bot.\nif you want your data deleted, please join the support server by doing !support"""
        result = await dbc.player.create(self.bot, ctx.author)
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
        playeruser = await self.bot.get_player(user.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        fish = await self.bot.get_fish(playeruser.trophy_oid)
        splitname = fish.name.split()
        fancy_rarity = await dbc.fish.fancy_rarity(fish.rarity)
        embed = discord.Embed(title=f"{fish.name}",url=f"https://www.fishbase.de/Summary/{splitname[0]}-{splitname[1]}.html", color=fancy_rarity[1])
        embed.set_author(name=f"{str(user)}'s trophy")
        embed.set_image(url=fish.image_url)
        embed.add_field(name='__Length__',value=f'{fish.original_length}cm')
        embed.add_field(name='__Rarity__',value=f'{fancy_rarity[0].upper()}')
        embed.add_field(name='__Worth__', value=f'{fish.coins(playeruser.trophy_rod_level)} coins')
        embed.set_footer(text=f"#{fish.db_position} out of 16206 catchable fish in the database")
        await ctx.reply(embed=embed)
    
    @commands.group(aliases=["rank","lb","leaderboard"], invoke_without_command=True, description="user leaderboards")
    async def top(self, ctx):
        await ctx.send_in_codeblock(f"please specify: {ctx.prefix}top (rod, coins, collection, caught)")
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["rods","r"])
    async def rod(self, ctx):
        playeruser = await self.bot.get_player(ctx.author.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        lvl = playeruser.rod_level
        cur = await self.bot.db.execute("SELECT * FROM f_users ORDER BY rodlevel DESC")
        topusers = await cur.fetchmany(10)
        step = 1
        table = ""
        for r in topusers:
            player = await self.bot.get_player(r[0])
            player_rod = await player.get_rod()
            table = table + f"{step}. {player.name} : {player_rod.name} (lvl {player_rod.level})\n"
            step += 1
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY rodlevel DESC) AS rodlevel FROM f_users) a WHERE userid = ?;",(player.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["coins","c"])
    async def coin(self, ctx):
        playeruser = await self.bot.get_player(ctx.author.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        cur = await self.bot.db.execute("SELECT * FROM f_users ORDER BY coins DESC")
        topusers = await cur.fetchmany(10)
        step = 1
        table = ""
        for r in topusers:
            player = await self.bot.get_player(r[0])
            table = table + f"{step}. {player.name} : {player.coins} coins)\n"
            step += 1
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY coins DESC) AS coins FROM f_users) a WHERE userid = ?;",(player.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["collections","cl"])
    async def collection(self, ctx):
        playeruser = await self.bot.get_player(ctx.author.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        step = 1
        table = ""
        c = await self.bot.db.execute("SELECT userid, COUNT(*) FROM f_collections GROUP BY userid")
        topusers = await c.fetchmany(10)
        c = await self.bot.db.execute("SELECT COUNT(*) FROM fishes")
        num_of_fish = await c.fetchone()
        for r in topusers:
            player = await self.bot.get_player(r[0])
            table = table + f"{step}. {player.name} : {r[1]}/{num_of_fish[0]})\n"
            step += 1
        c = await self.bot.db.execute("SELECT userid, COUNT(*) FROM f_collections GROUP BY userid")
        pos = 1
        for p in (await c.fetchall()):
            print(p[0])
            if p[0] == ctx.author.id:
                break
            else:
                pos += 1
        table = table + f"(your rank: #{pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["totalcaught","tc"])
    async def caught(self, ctx):
        playeruser = await self.bot.get_player(ctx.author.id)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        cur = await self.bot.db.execute("SELECT * FROM f_users ORDER BY totalcaught DESC")
        topusers = await cur.fetchmany(10)
        step = 1
        table = ""
        for r in topusers:
            player = await self.bot.get_player(r[0])
            table = table + f"{step}. {player.name} : {player.total_caught} total caught fish)\n"
            step += 1
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY totalcaught DESC) AS totalcaught FROM f_users) a WHERE userid = ?;",(player.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
            
def setup(bot):
    bot.add_cog(playermeta(bot))