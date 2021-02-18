import platform
import traceback
import asyncio
import time, math
import os, sys, random
import aiosqlite
import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check

from .utils import botchecks, dbc

class game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()   
    async def on_fish_catch(self, player, fish, coins):
        coins = round(coins,2)
        #first, lets update stats
        await self.bot.db.execute("UPDATE f_stats SET totalfished = (totalfished + 1)")
        await self.bot.db.execute("UPDATE f_stats SET totalcoinsearned = (totalcoinsearned + ?)",(coins,))
        self.bot.fishCaughtinsession += 1
        self.bot.coinsEarnedInSession += coins
        
        await self.bot.db.execute("UPDATE f_users SET coins = (coins + ?) WHERE userid = ?",(coins, player.id,))
        await self.bot.db.execute("UPDATE f_users SET totalcaught = (totalcaught + 1) WHERE userid = ?",(player.id,))
        await player.update_collection(fish.oid)
        await player.check_trophy(fish.oid)
        
    def select_3_reactions(self):
        image_list = {
            '🐬':"https://cdn.discordapp.com/attachments/342953709870776322/509381194031562756/file.jpg",
            '🐉':"https://cdn.discordapp.com/attachments/342953709870776322/509381159923220490/file.jpg",
            '🐳':"https://cdn.discordapp.com/attachments/342953709870776322/509381129934209046/file.jpg",
            '🐙':"https://cdn.discordapp.com/attachments/342953709870776322/509381101295239168/file.jpg",
            '🐡':"https://cdn.discordapp.com/attachments/342953709870776322/509381042210340879/file.jpg",
            '🐠':"https://cdn.discordapp.com/attachments/342953709870776322/509020495539077140/file.jpg",
            '🐋':"https://cdn.discordapp.com/attachments/342953709870776322/509020436118503446/file.jpg",
        }
        # return random.sample(list(image_list.items()), k=3)
        templist = image_list
        amount_to_remove = (len(templist) - 3) # to have 3 remaining
        for r in range(amount_to_remove):
            itr = random.choice(list(templist.keys()))
            templist.pop(itr, None)
        return templist
    
    def can_fish(self, userid):
        result = [i for i in self.bot.fishers if i == userid]
        if result == []:
            self.bot.fishers.append(userid)
            return True
        return False
    
    async def do_fish(self, ctx, player):
        msg = None
        got_it_correct = False
        fish = None
        threereactions = self.select_3_reactions()
        correct_emoji, correct_emoji_url = random.choice(list(threereactions.items()))
        initial_embed = discord.Embed(title="React with:")
        initial_embed.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        initial_embed.set_thumbnail(url=correct_emoji_url)
        msg = await ctx.send(embed=initial_embed)
        for r in list(threereactions.keys()):
            await msg.add_reaction(r[0])
        await asyncio.sleep(self.bot.seconds_to_react)
        updatedmsg = await ctx.channel.fetch_message(msg.id)
        cr = [r for r in updatedmsg.reactions if str(r) == correct_emoji]
        for u in (await cr[0].users().flatten()):
            if u.id == ctx.author.id:
                got_it_correct = True
                break
            else:
                continue
        if not got_it_correct:
            return await self.stop_fishing(ctx, updatedmsg)
        await msg.add_reaction('✅')
        await asyncio.sleep(0.5)
        fish = await ctx.random_fish(player.rod)
        splitname = fish.name.split()
        caught_before = "" if (await player.check_collection(fish.oid)) else " (NEW)"
        threereactions = self.select_3_reactions()
        correct_emoji, correct_emoji_url = random.choice(list(threereactions.items()))
        fancy_rarity = await dbc.fish.fancy_rarity(fish.rarity)
        embed = discord.Embed(title=f"{fish.name}{caught_before}",url=f"https://www.fishbase.de/Summary/{splitname[0]}-{splitname[1]}.html", color=fancy_rarity[1])
        embed.set_thumbnail(url=correct_emoji_url)
        embed.set_image(url=fish.image_url)
        embed.add_field(name='__Length__',value=f'{fish.original_length}cm')
        embed.add_field(name='__Rarity__',value=f'{fancy_rarity[0].upper()}')
        embed.add_field(name='__Coins Earned__', value=f'{round(((fish.coins(player.rod_level)) * self.bot.coin_multiplier), 3)} coins')
        await msg.edit(embed=embed)
        self.bot.dispatch("fish_catch", player, fish, round(((fish.coins(player.rod_level)) * self.bot.coin_multiplier), 3))
    
    async def stop_fishing(self, ctx, fishmsg):
        await fishmsg.add_reaction('🚫')
        try:
            self.bot.fishers.remove(ctx.author.id)
        except: pass
        return False
        
    async def start_fishing(self, ctx, fishmsg):
        self.bot.fishers.append(ctx.author.id)
    
    @commands.command(name="fish",description="fishy.py's fish game")
    async def fish(self, ctx):
        """The main fish game for Fishy.py.\nTo play, run the command, then click on the correct reaction shown in the embed. It will keep going over and over until you get it wrong."""
        player = await self.bot.get_player(ctx.author.id)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        can_fish = self.can_fish(ctx.author.id)
        if not can_fish:
            return await ctx.send_in_codeblock("you already fishing")
        while can_fish:
            r = await self.do_fish(ctx, player)
            if r is False or None:
                can_fish = False
                break
            else:
                continue
        return
    
    @fish.error
    async def on_fish_error(self, ctx, error):
        if isinstance(error, botchecks.FishNotFound):
            self.bot.fishers.remove(ctx.author.id)
            await ctx.send_in_codeblock(f"error while fishing, please try again, if this continues please join the support server ({ctx.prefix}support)")
            return
        else:
            await ctx.send_in_codeblock(f'Internal error, if this continues please join the support server ({ctx.prefix}support)')
        
    async def automatic_fishing(self, ctx):
        pass
        
    @commands.check(botchecks.ban_check)
    @commands.group(invoke_without_command=True, aliases=["af"], hidden=True)
    async def autofish(self, ctx):
        """The autofish command. Currently a WIP."""
        await ctx.send_in_codeblock("Coming soon")
                
def setup(bot):
    bot.add_cog(game(bot))