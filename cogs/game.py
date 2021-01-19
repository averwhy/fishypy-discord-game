import platform
import traceback
import asyncio
import time
import os, sys, random
import aiosqlite
import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check

from .utils import player, server, fish, botchecks

class game(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.image_list = {
            '🐬':"https://cdn.discordapp.com/attachments/342953709870776322/509381194031562756/file.jpg",
            '🐉':"https://cdn.discordapp.com/attachments/342953709870776322/509381159923220490/file.jpg",
            '🐳':"https://cdn.discordapp.com/attachments/342953709870776322/509381129934209046/file.jpg",
            '🐙':"https://cdn.discordapp.com/attachments/342953709870776322/509381101295239168/file.jpg",
            '🐡':"https://cdn.discordapp.com/attachments/342953709870776322/509381042210340879/file.jpg",
            '🐠':"https://cdn.discordapp.com/attachments/342953709870776322/509020495539077140/file.jpg",
            '🐋':"https://cdn.discordapp.com/attachments/342953709870776322/509020436118503446/file.jpg",
        }
        
    async def fish_success_update(self, author,guild,rarity,oid,flength): # this runs when the user fishes (successfully)
        if guild is not None: # fix to dm fish
            dbguild2 = server()
            dbguild = await self.bot.grab_server(guild.id)
            await dbguild2.update_caught_fish(guild)
            await dbguild2.check_trophy(data=dbguild,caughtoid=oid)
            
        dbuser = await self.bot.grab_db_user(author.id)
        
        user = player(dbuser)
        await user.update_caught_fish(userobject=author)
        
        await user.check_trophy(data=dbuser,caughtoid=oid)
        
        lvlbool = await user.update_xp(userobject=author,rarity=rarity)

        bot.fishCaughtinsession += 1
        return lvlbool
    
    def select_3_reactions(self):
        templist = self.image_list
        amount_to_remove = (len(templist) - 3) # to have 3 remaining
        for r in range(amount_to_remove):
            itr = random.choice(list(templist.keys()))
            templist.pop(itr, None)
        return templist
    
    def can_fish(self, userid):
        result = [i for i in self.bot.fishers if i == userid]
        if result == []:
            return True
        return False
    
    async def stop_fishing(self, ctx, fishmsg):
        await fishmsg.add_reaction('🚫')
    
    @commands.command(name="fish",description="fishy.py's fish game")
    async def fishbeta(self, ctx):
        checkuser = await self.bot.usercheck(ctx.author.id)
        if not checkuser:
            return await ctx.send_in_codeblock(f"I was unable to retrieve your profile. Have you done {ctx.prefix}start yet?", language='css')
        fishing = self.can_fish(ctx.author.id)
        while fishing:
            msg = None
            got_it_correct = None
            threereactions = self.select_3_reactions()
            cfish = await ctx.random_fish()
            correct_emoji, correct_emoji_url = random.choice(threereactions)
            rlist = []
            initial_embed = discord.Embed(title="React with:")
            initial_embed.set_thumbnail(url=correct_emoji_url)
            msg = await ctx.send(embed=initial_embed)
            for r in rlist:
                await ctx.message.add_reaction(r[0])
            def fish_check(r, u):
                nonlocal got_it_correct, correct_emoji
                if u == ctx.author and r.message == msg:
                    if str(r.emoji) == correct_emoji:
                        print("they got it right")
                        got_it_correct = True
                    else:
                        print("wrong lulw")
                        got_it_correct = False
                    return True
                return False
            try: reaction, user = await self.bot.wait_for('reaction_add', check=fish_check, timeout=self.bot.secondstoReact)
            except asyncio.TimeoutError:
                fishing = False
                await self.stop_fishing(ctx, msg)
                break
            if got_it_correct is False:
                fishing = False
                await self.stop_fishing(ctx, msg)
                break
            await msg.add_reaction('✅')
            await asyncio.sleep(0.7)
            await msg.edit(content="they caught a fish", embed=None)
        return
    
    @commands.check(botchecks.ban_check)
    @commands.group(invoke_without_command=True, aliases=["af"])
    async def autofish(self, ctx):
        await ctx.send_in_codeblock("Coming soon")


    # @commands.cooldown(1,7,BucketType.user)
    # @commands.check(botchecks.ban_check)
    # @commands.command(aliases=["f"])
    # async def fish(self, ctx): # the fish command. this consists of 1. checking if the user exists 2. if user exists, put together an embed and get a fish from DB using fish() class, 3. sends it and calls fish_update_success()
    #     authorid = ctx.author.id
    #     try:
    #         guildname = ctx.guild.name
    #         guildid = ctx.guild.id
    #     except: # dms, probably
    #         pass
    #     checkuser = await bot.usercheck(authorid)
    #     if checkuser == False:
    #         await ctx.send(f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
    #     else:
    #         embed = discord.Embed(title="**React to fish!**", description="", colour=discord.Colour(0x000000))
    #         msgtoedit = await ctx.send(embed=embed)
    #         await msgtoedit.add_reaction(emoji="\U0001f41f") # fish emoji
    #         await msgtoedit.add_reaction(emoji="\U0001f419") # octopus
    #         await msgtoedit.add_reaction(emoji="\U0001f420") # tropical fish
    #         reactionList = ["\U0001f41f","\U0001f419","\U0001f420"]
    #         def check(reaction, user):
    #             return user == ctx.message.author and str(reaction.emoji) in reactionList
    #         try:
    #             reaction, user = await bot.wait_for('reaction_add', timeout=bot.secondstoReact, check=check)
    #         except asyncio.TimeoutError:
    #             try:
    #                 await msgtoedit.clear_reactions()
    #                 embed = discord.Embed(title="**Timed out :(**", description="Fish again?", colour=discord.Colour(0x000000))
    #                 await msgtoedit.edit(embed=embed)
    #             except discord.errors.Forbidden:
    #                 pass
    #         else:
    #             try:
    #                 await msgtoedit.clear_reactions()
    #             except discord.errors.Forbidden:
    #                 pass
    #             f = fish()
    #             returnedlist = await f.randomfish()
    #             rarity = returnedlist[2]
    #             oid = returnedlist[0]
    #             flength = returnedlist[4]
    #             raritycalc2 = f.calculate_rarity(flength)
    #             user = player()
    #             await user.update_rarity_count(userobject=ctx.author,rarity=raritycalc2)
    #             lvl_up_bool = await fish_success_update(author=ctx.author,guild=ctx.message.guild,rarity=rarity,oid=oid,flength=flength)
    #             if lvl_up_bool is True:
    #                 await ctx.send(f"{ctx.author.mention}`, you leveled up!`")
    #             xp = float(rarity)
    #             xp2 = xp/100
    #             xp2 = round(xp2,5)
    #             embed = discord.Embed(title=f"**{returnedlist[5]}**", description="",url=returnedlist[1], colour=discord.Colour(0x00cc00))
    #             userdata = await self.bot.grab_db_user(ctx.author.id)
    #             currentxp = user.get_xp(userdata)
    #             levelbar = await self.bot.rodUpgradebar(userdata[3])
    #             embed.set_footer(text=f"{round(currentxp,3)}/1 XP [{levelbar}]",icon_url=(ctx.author.avatar_url))
    #             if bot.xp_multiplier == 1.0:
    #                 embed.add_field(name="__**XP Gained**__", value=f"{xp2}")
    #             else:
    #                 embed.add_field(name="__**XP Gained**__", value=f"{xp2} **x{bot.xp_multiplier}**")
    #             embed.add_field(name="__**Rarity**__",value=f"{raritycalc2}")
    #             embed.add_field(name="__**Length**__", value=f"{returnedlist[4]}cm")
    #             embed.add_field(name="__**# in database**__", value=f"{returnedlist[3]}/16205 fishes")
    #             embed.set_image(url=returnedlist[1])
    #             await msgtoedit.edit(embed=embed)
    #             print(f"{ctx.author.name} caught a {returnedlist[5]} in channel #{ctx.channel.name}, guild {ctx.guild.name} [user: {ctx.author.id}, channel {ctx.channel.id}, guild {ctx.guild.id}]")
    #             await asyncio.sleep(1)
    #             fish.reset_cooldown(ctx) # remove 7 second cooldown
                
def setup(bot):
    bot.add_cog(game(bot))