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

class fishing:
    async def randomfish(self): # Returns a random fish from the database.
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute('SELECT * FROM fishes ORDER BY RANDOM() LIMIT 1;')
            data = await c.fetchone()
            await db.commit()   
        return data
    async def getfish(self,oid):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(oid,))
            data = await c.fetchone()
            await db.commit()
        return data
    def calculate_rarity(self,length):
        raritycalc = float(length)
        raritycalc2 = None
        if raritycalc > 500:
            raritycalc2 = "Mythical"
        elif raritycalc > 200:
            raritycalc2 = "Legendary"
        elif raritycalc > 90:
            raritycalc2 = "Rare"
        elif raritycalc > 40:
            raritycalc2 = "Uncommon"
        elif raritycalc > 0:
            raritycalc2 = "Common"
        return raritycalc2

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
    async def update_caught_fish(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            await db.commit()
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("Update fishyusers set totalcaught = (totalcaught + 1) where userid = ?",(userobject.id,))
            await db.commit()   
        return
    async def check_trophy(self,data,caughtoid):
        usersid = data[0]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(caughtoid,))
            data2 = await c.fetchone()
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(data[4],))
            data = await c.fetchone()
            await db.commit()
        try:
            FishLengthFromTrophy = data[4]
            FishLengthJustCaught = data2[4]
            if float(FishLengthFromTrophy) < float(FishLengthJustCaught):
                async with aiosqlite.connect('fishypy.db') as db:
                    await db.execute("Update fishyusers set trophyoid = ? where userid = ?", (caughtoid, usersid,))
                    await db.commit()
                return
            else:
                #No updating needed
                return
        except:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("Update fishyusers set trophyoid = ? where userid = ?",(caughtoid,usersid,))
                await db.commit()
            print("user didnt have trophy so they got one")
            return
    async def add_user(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.name,))
            data = await c.fetchone()
            await db.commit()
            try:
                async with aiosqlite.connect('fishypy.db') as db:
                    #(userid integer, name text, totalcaught integer, Level real, trophyoid text, guildid integer, hexcolor text, reviewmsgid integer, commoncaught integer, uncommoncaught integer, rarecaught integer, legendarycaught integer, mythicalcaught integer)
                    await db.execute("INSERT INTO fishyusers VALUES (?,?,0,0.0,'None',?,'005dff', 0, 0, 0, 0, 0, 0)",(userobject.id,userobject.name,userobject.guild.id,))
                    await db.commit()
                return (f"`Done! Start fishing with {bot.defaultprefix}fish, or view your profile with {bot.defaultprefix}profile`")
            except Exception as e:
                return (f"`Something went wrong:` ```\n{e}\n```")
    async def update_review(self,userobject,reviewtext):
        try:
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
                data = await c.fetchone()
                await db.commit()
                
            if data is not None: # player exists
                stored_id = int(data[7])
                reviewchannel = bot.get_channel(735206051703423036)
                if reviewchannel is None:
                    reviewchannel = await bot.fetch_channel(735206051703423036)
                if stored_id != 0: # they have a review
                    msgtoedit = await reviewchannel.fetch_message(stored_id)
                    await msgtoedit.edit(content=f"Heres a review from {str(userobject)} ({userobject.id}):```\n{reviewtext}```")
                    return ("`Success! You've edited your review.")
                else: # they dont have a review
                    thereview = await reviewchannel.send(f"Heres a review from {userobject.mention} ({userobject.id}):```\n{reviewtext}```")
                    async with aiosqlite.connect('fishypy.db') as db:
                        await db.execute("Update fishyusers set reviewmsgid = ? where userid = ?",(thereview.id,userobject.id,))
                        await db.commit()
                        
                    return ("`Success! You can edit your review at any time using this command.`")
            else:
                return (f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
        except Exception as e:
            return (f"`{e}`")
    async def update_guild(self,userid,newguildid):
        try:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("UPDATE fishyusers SET guildid = ? WHERE userid = ?",(userid,newguildid,))
                await db.commit()
            return
        except Exception as e:
            return e
    async def db_ban(self,userobject,reason):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            await db.execute("INSERT INTO bannedusers VALUES (?,?,?)",(userobject.id,userobject.name,reason,))
            await db.commit()
        return
    async def db_unban(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            if data is not None:
                await db.execute("DELETE FROM bannedusers WHERE userid = ?",(userobject.id,))
                await db.commit()
    async def update_xp(self, userobject, rarity): # this entire method is a mess, i hate it lmao
        rarity = float(rarity)
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishyusers WHERE userid = ?",(userobject.id,))
            data = await c.fetchone() 
        theirlevel = float(data[3])
        theirlevel2 = divmod(float(data[3]),1)
        updatevalue = round(float(rarity),3) #rounds xp
        oldlevel = theirlevel2[0] #the level only, since divmod returns a tuple
        oldxp = theirlevel2[1]
        ##################################
        xptoadd = updatevalue / 100
        xptoadd = xptoadd * bot.xp_multiplier
        bot.xpgainedinsession += xptoadd
        updatevalue = theirlevel + xptoadd
        newlevel = divmod(float(updatevalue),1)
        newlevelint = int(newlevel[0])
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("UPDATE fishyusers SET Level = ? WHERE userid = ?",(updatevalue,userobject.id,))
            await db.commit()
        if newlevelint > int(oldlevel):
            return True
        else:
            return False
    async def update_profilecolor(self,hexstring,id):
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("UPDATE fishyusers SET hexcolor = ? WHERE userid = ?",(hexstring,id,))
            await db.commit()
        return
    async def update_rarity_count(self,userobject,rarity):
        raritycalc2 = None
        rarity = rarity.strip()
        if rarity == "Common":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyusers SET commoncaught = (commoncaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Mythical":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyusers SET mythicalcaught = (mythicalcaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Legendary":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyusers SET legendarycaught = (legendarycaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Rare":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyusers SET rarecaught = (rarecaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Uncommon":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE fishyusers SET uncommoncaught = (uncommoncaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        else:
            print("Sadge")
    
class playermeta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.check(is_owner) # <-- temp
    @commands.cooldown(1,30,BucketType.user)
    @customize.command(name="customize color", aliases=["c color"])
    async def color(self, ctx,hexcolor : str = None): # WIP
        authorid = ctx.message.author.id
        checkuser = await self.bot.usercheck(ctx.author.id)
        if checkuser is False:
            await ctx.send(f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
            return
        checkuser = await self.bot.usercheck(authorid)
        hexcolor = hexcolor.upper()
        newhexcolor = int((f"0x{hexcolor}"),0)
        print(newhexcolor)
        if hexcolor is None:
            await ctx.send("`Please provide a valid hex color value! (Without the #)`")
            return
        else:
            # try:
            embed = discord.Embed(title="<-- Theres a preview of your chosen color!", description=f"**Are you sure you would like to change your profile color to hex value {hexcolor}?**", colour=discord.Color(newhexcolor))
            askmessage = await ctx.send(embed=embed)
            await askmessage.add_reaction(emoji="\U00002705") # white check mark

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == "\U00002705"
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
            except asyncio.TimeoutError:
                try:
                    await askmessage.clear_reactions()
                except: # forbidden (most likely)
                    pass
                mbed = discord.Embed(title="Timed out :(", description=f"Try again?", colour=discord.Colour(0xfcd703))
                await askmessage.edit(embed=mbed)
                return
            else:
                try:
                    await askmessage.clear_reactions()
                except: # forbidden (most likely)
                    await askmessage.delete() # we'll just delete our message /shrug
                dbuser = db_user()
                await dbuser.update_profilecolor(hexcolor,ctx.author.id)
                await ctx.send(f"`Success! Do {bot.defaultprefix}profile to see your new profile color.`")
                # TODO
            # except:
            #     embed = discord.Embed(title="Something went wrong...", description=f"Please input a valid hex value. See [this color picker](https://htmlcolorcodes.com/color-picker/) if you need help.", colour=discord.Colour(0xfcd703))
            #     embed.set_footer(text=f"Fishy.py - v{bot.version}",icon_url=(bot.user.avatar_url))
            #     msgtoedit = await ctx.send(embed=embed)
            
    @commands.check(ban_check)
    @commands.command(aliases=["prof","me"])
    async def profile(self, ctx, user: discord.User = None): # profile command
        dbuser = db_user()
        tfish = fishing()
        c_f =  str(discord.PartialEmoji(name="common_fish", id=770254565777866782, animated=False))
        uc_f =  str(discord.PartialEmoji(name="uncommon_fish", id=770254565642731531, animated=False))
        r_f =  str(discord.PartialEmoji(name="rare_fish", id=770254565462376459, animated=False))
        l_f =  str(discord.PartialEmoji(name="legendary_fish", id=770254565793857537, animated=False))
        m_f =  str(discord.PartialEmoji(name="mythical_fish", id=770254565852315658, animated=False))
        if user is None:
            user = ctx.author
        checkuser = await self.bot.usercheck(user.id)
        if checkuser is False:
            await ctx.send(f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
            return
        returnedlist = await self.bot.grab_db_user(user.id)
        theirguildid = int(returnedlist[5])
        newhexcolor = int((f"0x{returnedlist[6]}"),0)
        embed = discord.Embed(title=f"**{returnedlist[1]}**", description=f"*ID:{returnedlist[0]}*", colour=discord.Colour(newhexcolor))
        embed.set_footer(text=f"Fishy.py - v{bot.version}",icon_url=(bot.user.avatar_url))
        users_levelandxp = returnedlist[3]
        users_levelandxp = float(users_levelandxp)
        levelmath = divmod(users_levelandxp,1)
        user_level = levelmath[0]
        embed.add_field(name="User Level", value=f"{int(user_level)}")
        embed.add_field(name="XP",value=f"{round(levelmath[1],3)}")
        embed.add_field(name="Total fish caught", value=f"{int(returnedlist[2])}")
        async with aiosqlite.connect("fishypy.db") as db:
            c = await db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY Level DESC) AS Level FROM fishyusers) a WHERE userid = ?",(user.id,)) # i love this statement
            data1 = await c.fetchone()
            c = await db.execute("SELECT * FROM fishyusers")
            data2 = await c.fetchall()
            await db.commit()
            
        embed.add_field(name="Rank", value=f"#{data1[1]} out of {len(data2)} users")
        try:
            returnedusersguild = bot.get_guild(theirguildid)
            if returnedusersguild is None:
                returnedusersguild = await bot.fetch_guild(theirguildid)
            embed.add_field(name="Guild", value=f"{returnedusersguild.name}")
        except discord.errors.Forbidden:
            embed.add_field(name="Guild", value=f"The bot is no longer in this guild, therefore i cannot get it's information.")
        embed.add_field(name="Caught fish per type",value=f"{c_f}:{returnedlist[8]}      {uc_f}:{returnedlist[9]}      {r_f}:{returnedlist[10]}      {l_f}:{returnedlist[11]}      {m_f}:{returnedlist[12]}",inline=False)
        trophyOID = returnedlist[4]
        tdata = await self.bot.grab_db_user(user.id)
        data = await dbuser.get_trophy(data=tdata)
        if data is None:
            tvalue = "You have no Trophy! Try fishing!"
        else:
            tvalue = (f"**{data[5]}** at **{data[4]}cm**")
            embed.set_image(url=data[1])
        embed.add_field(name="Trophy", value=f"{tvalue}",inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)
        
    @commands.check(ban_check)
    @commands.check(is_in_guild)
    @bot.command()
    async def start(self, ctx): # adds users to DB so they can fish
        async with ctx.channel.typing():
            authorid = ctx.message.author.id
            authorname = ctx.message.author.name
            guildid = ctx.message.guild.id 
            guildname = ctx.message.guild.name
            data = await self.bot.grab_db_user(authorid)
            if data is None:
                user = db_user()
                returnedmsg = await user.add_user(userobject=ctx.author)
                await asyncio.sleep(1) # to ease potential ratelimits
                await ctx.send(returnedmsg)
            else:
                #user exists
                await ctx.send(f"`You're already in the database, {ctx.author.name}`")
      
    @commands.check(ban_check)
    @commands.cooldown(1,5,BucketType.user)
    @commands.command()
    async def trophy(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        authorid = user.id
        checkuser = await self.bot.usercheck(authorid)
        if checkuser is not False:
            data1 = await self.bot.grab_db_user(authorid)
            dbuser = db_user()
            data = await dbuser.get_trophy(data1)
            if data is None:
                embed = discord.Embed(title=f"You dont have a Trophy!",description="Try Fishing!")
            else:
                embed = discord.Embed(title=f"{user.name}'s Trophy",url=data[1],colour=discord.Colour(0x00cc00))
                tvalue = (f"**{data[5]}** at **{data[4]}cm**")
                embed.set_image(url=data[1])
                f = fishing()
                raritycalc = f.calculate_rarity(data[4])
                dbPos = data[3]
                embed.add_field(name=tvalue,value=f"{raritycalc}({data[4]} cm), #{dbPos} in database")
            await ctx.send(embed=embed)
                
    @commands.check(ban_check)
    @commands.cooldown(1,300,BucketType.user)
    @bot.command()
    async def review(self, ctx, *, reviewtext): # review command. Sends a message to fishypy guild and saves that message ID in db. If user has sent a review it checks for that and edits it if it exists.
        authorid = ctx.message.author.id
        authorname = ctx.message.author.name
        checkuser = await self.bot.usercheck(authorid)
        if checkuser is not False:
            data = await self.bot.grab_db_user(id=authorid)
            user = db_user()
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
                user = db_user()
                m = await user.update_review(userobject=ctx.author,reviewtext=reviewtext)
                # and then
                await askmessage.clear_reactions()
                await askmessage.edit(content=m)   
        else:
            await ctx.send(f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")