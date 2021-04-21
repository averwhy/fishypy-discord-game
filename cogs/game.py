import asyncio
import random
from typing import Any
import discord
from datetime import datetime, timedelta
from discord.ext import commands
import humanize

from .utils import botchecks, dbc

class game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()   
    async def on_fish_catch(self, player, fish, coins, autofish: bool = False):
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
        
        if autofish:
            await self.bot.db.execute("UPDATE f_stats SET totalautofished = (totalautofished + 1)")
        await self.bot.db.commit()
        
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
        if not userid in self.bot.fishers:
            self.bot.fishers.append(userid)
            return True
        return False
    
    async def do_autofishing(self, ctx, player):
        playernet = await player.get_net()
        actual_start = datetime.utcnow()
        time_end = datetime.utcnow() + timedelta(minutes=playernet.minutes)
        caught = 0
        coins = 0
    
        while ctx.author.id in self.bot.autofishers and datetime.utcnow() < time_end:
            fish = await ctx.random_fish(player.rod)
            splitname = fish.name.split()
            caught_before = "" if (await player.check_collection(fish.oid)) else " (NEW)"
            coin_bonus = "" if self.bot.coin_multiplier == 1.0 else f" **x{self.bot.coin_multiplier}**"
            fancy_rarity = await dbc.fish.fancy_rarity(fish.rarity)
            coins_earned = round(((fish.coins(player.rod_level)) * self.bot.coin_multiplier), 3)
            embed = discord.Embed(title=f"{fish.name}{caught_before}",url=f"https://www.fishbase.de/Summary/{splitname[0]}-{splitname[1]}.html", color=fancy_rarity[1])
            embed.set_image(url=fish.image_url)
            embed.add_field(name='__Length__',value=f'{fish.original_length}cm')
            embed.add_field(name='__Rarity__',value=f'{fancy_rarity[0].upper()}')
            embed.add_field(name='__Coins Earned__', value=f'{round((coins_earned - (coins_earned * 0.10)),2)} coins{coin_bonus}')
            
            coins += round(coins_earned,2)
            caught += 1
            
            if fish.rarity > dbc.EXTREMELY_RARE:
                if player.autofishing_notif <= 4: 
                    await player.user.send(embed=embed)
            elif fish.rarity > dbc.VERY_RARE:
                if player.autofishing_notif <= 3:
                    await player.user.send(embed=embed)
            elif fish.rarity > dbc.RARE:
                if player.autofishing_notif <= 2:
                    await player.user.send(embed=embed)
            elif fish.rarity > dbc.COMMON:
                if player.autofishing_notif <= 1:
                    await player.user.send(embed=embed)
            else:
                pass
            self.bot.dispatch("fish_catch", player, fish, (coins_earned - (coins_earned * 0.10)), autofish=True)
            await asyncio.sleep(10)

        actual_fishing_time = f"(actual time {humanize.precisedelta(actual_start)})" if player.id not in self.bot.autofishers else ""
        stopped_or_cancelled = "FINISHED" if player.id in self.bot.autofishers else "CANCELLED"
        try: self.bot.autofishers.remove(player.id)
        except ValueError: pass
        
        await player.user.send(f"```md\n#____________AUTOFISHING {stopped_or_cancelled}____________#\nfishing time: {playernet.minutes} minutes {actual_fishing_time}\nfish caught: {caught}\ncoins eared: {coins}\n```")
        return
    
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
        await asyncio.sleep(0.3)
        fish = await ctx.random_fish(player.rod)
        splitname = fish.name.split()
        caught_before = "" if (await player.check_collection(fish.oid)) else " (NEW)"
        coin_bonus = "" if self.bot.coin_multiplier == 1.0 else f" **x{self.bot.coin_multiplier}**"
        fancy_rarity = await dbc.fish.fancy_rarity(fish.rarity)
        embed = discord.Embed(title=f"{fish.name}{caught_before}",url=f"https://www.fishbase.de/Summary/{splitname[0]}-{splitname[1]}.html", color=fancy_rarity[1])
        embed.set_thumbnail(url=correct_emoji_url)
        embed.set_image(url=fish.image_url)
        embed.add_field(name='__Length__',value=f'{fish.original_length}cm')
        embed.add_field(name='__Rarity__',value=f'{fancy_rarity[0].upper()}')
        embed.add_field(name='__Coins Earned__', value=f'{round(((fish.coins(player.rod_level)) * self.bot.coin_multiplier), 3)} coins{coin_bonus}')
        await msg.edit(embed=embed)
        self.bot.dispatch("fish_catch", player, fish, round(((fish.coins(player.rod_level)) * self.bot.coin_multiplier), 3), autofish=False)
    
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
        player = await self.bot.get_player(ctx.author)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        can_fish = self.can_fish(ctx.author.id)
        if not can_fish:
            return await ctx.send_in_codeblock("you already fishing")
        while ctx.author.id in self.bot.fishers:
            r = await self.do_fish(ctx, player)
            if r is False or None:
                can_fish = False
                break
            else:
                continue
        return
    
    @fish.error
    async def on_fish_error(self, ctx, error):
        self.bot.fishers.remove(ctx.author.id)
        if isinstance(error, botchecks.FishNotFound):
            await ctx.send_in_codeblock(f"error while fishing, please try again, if this continues please join the support server ({ctx.prefix}support)")
            return
        else:
            await ctx.send_in_codeblock(f'Internal error, if this continues please join the support server ({ctx.prefix}support)')
    
      
    @commands.group(invoke_without_command=True, aliases=["af"], description="idle fishing, catches are sent in DM")
    async def autofish(self, ctx):
        """The base autofish command. Invoking with no subcommand shows autofishing stats."""
        player = await self.bot.get_player(ctx.author)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        playernet = await player.get_net()
        is_fishing = ctx.author.id in self.bot.autofishers
        fancy_af_notif = player.fancy_af_notif()
        summary = [f"autofishing: {str(is_fishing).lower()}"]
        summary.append(f"notifications level: {player.autofishing_notif} ({fancy_af_notif})")
        summary.append(f"minutes you can autofish: {playernet.minutes}")
        await ctx.send_in_codeblock(content="\n".join(summary))
    
    @autofish.command()
    async def start(self, ctx):
        """starts autofishing"""
        player = await self.bot.get_player(ctx.author)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        is_fishing = ctx.author.id in self.bot.autofishers
        if is_fishing:
            return await ctx.send_in_codeblock(f"you are already autofishing, check [ {ctx.prefix}autofish ] for more info", language='ini')
        
        await ctx.message.add_reaction("✅")
        await ctx.send_in_codeblock("autofishing started, please allow dm's from bot")
        self.bot.autofishers.append(ctx.author.id)
        return await self.do_autofishing(ctx, player)
        
    @autofish.command(aliases=["quit", "cancel", "fuckoff"])
    async def stop(self, ctx):
        """stops/cancels autofishing. autofishing stats take up 10 seconds to send."""
        player = await self.bot.get_player(ctx.author)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        is_fishing = ctx.author.id in self.bot.autofishers
        if not is_fishing:
            return await ctx.send_in_codeblock(f"you can't stop autofishing if you aren't autofishing in the first place")
        
        try: self.bot.autofishers.remove(ctx.author.id)
        except ValueError: pass
        return await ctx.send_in_codeblock("autofishing stopped, check your dm's for more information")
    
    @autofish.command(aliases=["s"])
    async def settings(self, ctx):
        """shows notification settings for autofishing"""
        player = await self.bot.get_player(ctx.author)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        l1 = "✓" if player.autofishing_notif == 1 else "x"
        l2 = "✓" if player.autofishing_notif == 2 else "x"
        l3 = "✓" if player.autofishing_notif == 3 else "x"
        l4 = "✓" if player.autofishing_notif == 4 else "x"
        l5 = "✓" if player.autofishing_notif == 5 else "x"
        await ctx.send_in_codeblock(f"""#______DM NOTIFICATIONS______#
[without notification][{l5}](!set 5)
[extremely rare only][{l4}](!set 4)
[very rare and above][{l3}](!set 3)
[rare and above][{l2}](!set 2)
[all catches][{l1}](!set 1)""",
language='md')
        

    @autofish.command(name="set", description="change autofishing notification settings")
    async def _set(self, ctx, level: int = None):
        """sets your notification level for autofishing, see the settings subcommand for all options"""
        """set your autofish notification level (1-5), see the 'af settings' command for all options"""
        player = await self.bot.get_player(ctx.author)
        if player is None: return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        if level is None:
            return await ctx.send_in_codeblock(f"please specify {ctx.prefix}set 1-5 , check [ {ctx.prefix}autofish settings ] for all info",language='ini')
        if level > 5:
            return await ctx.send_in_codeblock(f"invalid option , check [ {ctx.prefix}autofish settings ] for all info",language='ini')
        
        await self.bot.db.execute("UPDATE f_users SET autofishingnotif = ? WHERE userid = ?", (level, ctx.author.id,))
        await self.bot.db.commit()
        return await ctx.send_in_codeblock("done", language='css')
                
def setup(bot):
    bot.add_cog(game(bot))