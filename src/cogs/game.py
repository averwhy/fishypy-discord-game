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
            
#####################################################################################################################################################################
            
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

async def rodUpgradebar(rodlvl): # upgrade bar PogU Clap
    return f"{'#' * (decimal := round(rodlvl % 1 * 15))}{'_' * (15 - decimal)}"
    #print(returned_upgradeBar)   

#######################################################################################################################################################
#NOW FOR THE ACUTAL COG                                                                                                                               #
#######################################################################################################################################################

class game(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    async def fish_success_update(self, author,guild,rarity,oid,flength): # this runs when the user fishes (successfully)
        if guild is not None: # fix to dm fishing
            dbguild2 = db_guild()
            dbguild = await self.bot.grab_db_guild(guild.id)
            await dbguild2.update_caught_fish(guild)
            await dbguild2.check_trophy(data=dbguild,caughtoid=oid)
            
        dbuser = await self.bot.grab_db_user(author.id)
        
        user = db_user()
        await user.update_caught_fish(userobject=author)
        
        await user.check_trophy(data=dbuser,caughtoid=oid)
        
        lvlbool = await user.update_xp(userobject=author,rarity=rarity)

        bot.fishCaughtinsession += 1
        return lvlbool
    
    @commands.check(ban_check)
    @bot.group(invoke_without_command=True,aliases=["af","autofishing"])
    async def autofish(self, ctx):
        await ctx.send("`Coming soon!`")

    @commands.cooldown(1,7,BucketType.user)
    @commands.check(ban_check)
    @commands.command(aliases=["f"])
    async def fish(self, ctx): # the fishing command. this consists of 1. checking if the user exists 2. if user exists, put together an embed and get a fish from DB using fishing() class, 3. sends it and calls fish_update_success()
        authorid = ctx.author.id
        try:
            guildname = ctx.guild.name
            guildid = ctx.guild.id
        except: # dms, probably
            pass
        checkuser = await bot.usercheck(authorid)
        if checkuser == False:
            await ctx.send(f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
        else:
            embed = discord.Embed(title="**React to fish!**", description="", colour=discord.Colour(0x000000))
            msgtoedit = await ctx.send(embed=embed)
            await msgtoedit.add_reaction(emoji="\U0001f41f") # fish emoji
            await msgtoedit.add_reaction(emoji="\U0001f419") # octopus
            await msgtoedit.add_reaction(emoji="\U0001f420") # tropical fish
            reactionList = ["\U0001f41f","\U0001f419","\U0001f420"]
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in reactionList
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
            except asyncio.TimeoutError:
                try:
                    await msgtoedit.clear_reactions()
                    embed = discord.Embed(title="**Timed out :(**", description="Fish again?", colour=discord.Colour(0x000000))
                    await msgtoedit.edit(embed=embed)
                except discord.errors.Forbidden:
                    pass
            else:
                try:
                    await msgtoedit.clear_reactions()
                except discord.errors.Forbidden:
                    pass
                f = fishing()
                returnedlist = await f.randomfish()
                rarity = returnedlist[2]
                oid = returnedlist[0]
                flength = returnedlist[4]
                raritycalc2 = f.calculate_rarity(flength)
                user = db_user()
                await user.update_rarity_count(userobject=ctx.author,rarity=raritycalc2)
                lvl_up_bool = await fish_success_update(author=ctx.author,guild=ctx.message.guild,rarity=rarity,oid=oid,flength=flength)
                if lvl_up_bool is True:
                    await ctx.send(f"{ctx.author.mention}`, you leveled up!`")
                xp = float(rarity)
                xp2 = xp/100
                xp2 = round(xp2,5)
                embed = discord.Embed(title=f"**{returnedlist[5]}**", description="",url=returnedlist[1], colour=discord.Colour(0x00cc00))
                userdata = await self.bot.grab_db_user(ctx.author.id)
                currentxp = user.get_xp(userdata)
                levelbar = await rodUpgradebar(userdata[3])
                embed.set_footer(text=f"{round(currentxp,3)}/1 XP [{levelbar}]",icon_url=(ctx.author.avatar_url))
                if bot.xp_multiplier == 1.0:
                    embed.add_field(name="__**XP Gained**__", value=f"{xp2}")
                else:
                    embed.add_field(name="__**XP Gained**__", value=f"{xp2} **x{bot.xp_multiplier}**")
                embed.add_field(name="__**Rarity**__",value=f"{raritycalc2}")
                embed.add_field(name="__**Length**__", value=f"{returnedlist[4]}cm")
                embed.add_field(name="__**# in database**__", value=f"{returnedlist[3]}/16205 fishes")
                embed.set_image(url=returnedlist[1])
                await msgtoedit.edit(embed=embed)
                print(f"{ctx.author.name} caught a {returnedlist[5]} in channel #{ctx.channel.name}, guild {ctx.guild.name} [user: {ctx.author.id}, channel {ctx.channel.id}, guild {ctx.guild.id}]")
                await asyncio.sleep(1)
                fish.reset_cooldown(ctx) # remove 7 second cooldown
                
def setup(bot):
    bot.add_cog(game(bot))