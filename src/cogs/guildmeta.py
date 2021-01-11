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

class db_guild:
    #(guildid text, totalcaught text, globalpos text, topuser text, guildtrophyoid text)
    def __init__(self): #init func is useless because it cant be async Pepepains
        pass
    def get_caughtfish(self,data):
        return data[2]
    async def get_trophy(self,data):
        trophyoid = data[3]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(trophyoid,))
            returndata = await c.fetchone()
            await db.commit()
        return returndata
    async def add_guild(self,guildobject):
        async with aiosqlite.connect('fishypy.db') as db:
            #(guildid integer, guildname text, totalcaught integer , guildtrophyoid text, commoncaught integer, uncommoncaught integer, rarecaught integer, legendarycaught integer, mythicalcaught integer)
            await db.execute(f"INSERT INTO fishyguilds VALUES (?,?,0,'None', 0, 0, 0, 0, 0,'False')",(guildobject.id,guildobject.name,))
            await db.commit()
        return
    async def check_trophy(self,data,caughtoid):
        guildsid = data[0]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(caughtoid,))
            data2 = await c.fetchone()
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(data[3],))
            data = await c.fetchone()
            await db.commit()
            print(data)
        try:
            FishLengthFromTrophy = data[6]
            FishLengthJustCaught = data2[6]
            print(f"{FishLengthFromTrophy} vs {FishLengthJustCaught}")
            if float(FishLengthFromTrophy) < float(FishLengthJustCaught): # this will error if trophy length is None, which triggers except below 
                async with aiosqlite.connect('fishypy.db') as db:
                    await db.execute("Update fishyguilds set guildtrophyoid = ? where guildid = ?", (caughtoid, guildsid,))
                    await db.commit()
                return
            else:
                #No updating needed
                return
        except:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("Update fishyguilds set guildtrophyoid = ? where guildid = ?",(caughtoid,guildsid,))
                await db.commit()
            print("user didnt have trophy so they got one")
            return
    async def update_caught_fish(self,guildobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyguilds WHERE guildid = ?",(guildobject.id,))
            data = await c.fetchone()
            await db.commit()
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("Update fishyguilds set totalcaught = (totalcaught + 1) where guildid = ?",(guildobject.id,))
            await db.commit()   
        return
    async def update_rarity_count(self,guildobject,rarity):
        userobject = guildobject
        rarity = rarity.strip()
        if rarity == "Common":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyguilds SET commoncaught = (commoncaught + 1) WHERE guildid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Mythical":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyguilds SET mythicalcaught = (mythicalcaught + 1) WHERE guildid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Legendary":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyguilds SET legendarycaught = (legendarycaught + 1) WHERE guildid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Rare":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyguilds SET rarecaught = (rarecaught + 1) WHERE guildid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Uncommon":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyguilds SET uncommoncaught = (uncommoncaught + 1) WHERE guildid = ?",(userobject.id,))
                await db.commit()
        else:
            print("Sadge")
            
class db_user:
    def __init__(self, bot): #init func is useless because it cant be async Pepepains
        self.bot = bot
    async def get_trophy(self,data):
        trophyoid = data[4]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(trophyoid,))
            returndata = await c.fetchone()
            await db.commit()
        return returndata
    def get_caughtfish(self,data):
        fishescaught = data[2]
        return fishescaught
    def get_level(self,data):
        x = float(data[3])
        usermath = divmod(x,1)
        userlevel = usermath[0]
        return userlevel
    def get_xp(self,data):
        xpmath = divmod(data[3],1)
        userxp = xpmath[1]
        return userxp
    def get_guild_obj(self,data):
        guildid = data[6]
        guildobj = bot.get_guild(guildid)
        return guildobj
    def get_review_id(self,data):
        reviewid = data[8]
        return reviewid
    ##Now for updates n stuff
    #This is stripped down because i dont need anything else
    async def update_guild(self,userid,newguildid):
        try:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("UPDATE fishyusers SET guildid = ? WHERE userid = ?",(userid,newguildid,))
                await db.commit()
            return
        except Exception as e:
            return e

class guildmeta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logchannel = bot.get_channel(761683999772377128)
        if logchannel is None:
            logchannel = await bot.fetch_channel(761683999772377128)
        await logchannel.send(f"I am now in the `{guild.name} [{guild.id}]` guild!")
        data = await self.bot.grab_db_guild(guild.id)
        if data is None: # prevent duplicate guilds
            dbguild = db_guild()
            await dbguild.add_guild(guild)
        else:
            return
        
    @commands.check(ban_check)
    @commands.cooldown(1,60,BucketType.user)
    @commands.command()
    async def guild(self, ctx, server: int = None):
        authorid = ctx.message.author.id
        authorname = ctx.message.author.name
        if ctx.guild is None:
            await ctx.send("`Error: You didnt specify a guild, and are running this command in a DM!`")
            return
        dbguild = db_guild()
        if server is None:
            guildid = ctx.message.guild.id
            data = await self.bot.grab_db_user(authorid)
            guildidtograb = int(data[5])
            returnedlist = await self.bot.grab_db_guild(guildidtograb)
            async with aiosqlite.connect("fishypy.db") as db:
                c = await db.execute("SELECT * FROM (SELECT guildid, RANK() OVER (ORDER BY totalcaught DESC) AS totalcaught FROM fishyguilds) a WHERE guildid = ?;",(ctx.message.guild.id,)) # i love this statement
                data1 = await c.fetchone()
                c = await db.execute("SELECT * FROM fishyguilds")
                data2 = await c.fetchall()
                await db.commit()
            grabbedguild = bot.get_guild(guildidtograb)
            if grabbedguild is None:
                grabbedguild = await bot.fetch_guild(int(returnedlist[0]))
            embed = discord.Embed(title=f"**{grabbedguild.name}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(0x242424))
            embed.set_footer(text=f"Fishy.py - v{bot.version}",icon_url=(bot.user.avatar_url))
            embed.add_field(name="Total fish caught", value=f"{returnedlist[2]}")   
            embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} guilds")
            async with aiosqlite.connect("fishypy.db") as db:
                c = await db.execute("SELECT * FROM fishyusers WHERE guildid = ? ORDER BY Level DESC",(grabbedguild.id,))
                data3 = await c.fetchone()
            users_levelandxp = data3[3]
            users_levelandxp = float(users_levelandxp)
            levelmath = divmod(users_levelandxp,1)
            embed.add_field(name="Top user",value=f"{data3[1]}, at level {int(levelmath[0])}",inline=False)
            # print(levelmath)
            trophyOID = returnedlist[5]
            data = await dbguild.get_trophy(data=returnedlist)
            if data is None:
                tvalue = "This guild has no trophy!"
            else:
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
            embed.add_field(name="Trophy", value=f"{tvalue}",inline=False)
            embed.set_thumbnail(url=grabbedguild.icon_url)
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send("`Sorry, viewing other guild profiles via ID is temporarily unavaliable.`")
    
    @commands.check(ban_check)
    @commands.cooldown(1,300,BucketType.user)
    @commands.group(aliases=["c","change","custom"],invoke_without_command=True)
    async def customize(self, ctx):
        #await ctx.send("`Youre missing one of the below params:` ```md\n- guild\n- color\n```")
        customize.reset_cooldown(ctx)
    
    @customize.command(name="guild")
    async def gld(self, ctx, newguild: int = None):
        dbuser = db_user()
        if newguild is None:
            askmessage = await ctx.send(f"`Are you sure you want to change your guild to this server?`")
            await askmessage.add_reaction(emoji="\U00002705") # white check mark
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
            except asyncio.TimeoutError:
                await askmessage.edit(content="`Prompt timed out. Try again`")
            else:
                try:
                    await askmessage.clear_reactions()
                except:
                    print(f"Failed to remove reactions in guild {ctx.message.guild.name} ({ctx.message.guild.id}), channel #{ctx.message.channel.name}")
                await ctx.send(f"`Success! You now belong to {ctx.guild.name}!`")
        if newguild is not None:
            try:
                grabbed_guild = bot.get_guild(newguild)
                if grabbed_guild is None:
                    grabbed_guild = await bot.fetch_guild(newguild)
            except Exception as e:
                await ctx.send(f"`I couldn't find that guild. More info:` ```\n{e}\n```")
                return # cancels rest of function
            askmessage = await ctx.send(f"`Are you sure you want to change your guild to {grabbed_guild.name}?`")
            await askmessage.add_reaction(emoji="\U00002705") # white check mark
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
            except asyncio.TimeoutError:
                await askmessage.edit(content="`Prompt timed out. Try again`")
            else:
                try:
                    await askmessage.clear_reactions()
                except:
                    print(f"Failed to remove reactions in guild {ctx.message.guild.name} ({ctx.message.guild.id}), channel #{ctx.message.channel.name}")
                m = await dbuser.update_guild(ctx.author.id, newguild)
                if m is None:
                    await askmessage.edit(content=f"`Success! You now belong to {grabbed_guild.name}!`")
                else:
                    await askmessage.edit(content=f"Something went wrong: ```\n{m}\n```")
