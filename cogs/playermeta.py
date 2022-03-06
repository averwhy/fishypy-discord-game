# pylint: disable=wrong-import-order, missing-function-docstring, invalid-name, broad-except, too-many-branches, too-many-statements, too-many-locals, 
import random
import discord
from discord.ext import commands, menus
from discord.ext.commands.cooldowns import BucketType
from .utils import botchecks, botmenus, dbc
OWNER_ID = 267410788996743168

class playermeta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            if (await self.bot.usercheck(before.id)):
                await self.bot.db.execute("UPDATE f_users SET name = ? WHERE userid = ?")
                await self.bot.db.commit()
    
    @commands.check(botchecks.ban_check)
    @commands.command(aliases=["prof","me"], description="player profile, rod level, collection")
    async def profile(self, ctx, user: discord.User = None): # profile command
        """shows you your player profile (coins, collection, total caught, trophy, etc). \nyou can also view other users profiles, for example !profile @Fishy.py"""
        if user is None:
            user = ctx.author
        playeruser = await self.bot.get_player(user)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        collection_length = await self.bot.db.execute("SELECT COUNT(*) FROM f_collections WHERE userid = ?",(user.id,))
        is_verified = "  <:verified:826441930254057493>" if (await self.bot.is_verified(user)) else ""
        is_dev = "  <:developer:826440754809012244>" if user.id in [OWNER_ID, 163247205757616128] else ""
        is_bughunter = "  <:bughunter:826483661552484352>" if user.id in [267410788996743168, 187056629223522305, 715143242093690931, 610904174636564500, 443791364073848833] else ""
        is_staff = "  <:stafftools:826487050366353408>" if user.id in [267410788996743168, 163247205757616128, 509560211460194335, 708715777993211926] else ""
        embed = discord.Embed(title=f"{user.name}{is_dev}{is_verified}{is_staff}{is_bughunter}")
        embed.add_field(name="__Coins__", value=round(playeruser.coins,2))
        embed.add_field(name="__Collection__", value=(await playeruser.get_collection()))
        embed.add_field(name="__Total Caught__", value=f"{playeruser.total_caught} fish")
        playerrod = await playeruser.get_rod()
        embed.add_field(name="__Rod__", value=f"**{playerrod.name}** (Max length {playerrod.max_length}cm)")
        playernet = await playeruser.get_net()
        embed.add_field(name="__Net__", value=f"**{playernet.name}** (Autofishing mins: {playernet.mins})")
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
        if not result:
            await ctx.reply_in_codeblock(f"you're already in the database\nhowever, you can also delete all of your data if you wish. to do this, run the command [{ctx.prefix}removeme]")
            
    @commands.command(hidden=True, aliases=["optout","deleteme","stop"])
    async def removeme(self, ctx):
        """deletes all of your data from the bot. this is completely irreversible."""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        confirm = await ctx.send_in_codeblock("- warning! deleting all of your data is absolutely irreversible.\nyou will lose your entire profile (coins, rods, nets, caught fish, collection, position on leaderboards, etc)\nyou cannot go back. are you sure you want all of your data to be deleted?",language='diff')
        did_they = await self.bot.prompt(ctx.author.id, confirm, timeout=15)
        if did_they:
            await self.bot.db.execute("DELETE FROM f_users WHERE userid = ?", (ctx.author.id,))
            await self.bot.db.execute("DELETE FROM f_collections WHERE userid = ?", (ctx.author.id,))
            await self.bot.db.commit()
            await ctx.reply_in_codeblock("done, i've deleted all of your data.")
        if not did_they:
            await ctx.reply_in_codeblock("cancelled. none of your data was deleted.")
      
    @commands.check(botchecks.ban_check)
    @commands.cooldown(1,5,BucketType.user)
    @commands.command(description="views your or someone elses trophy")
    async def trophy(self, ctx, user: discord.User = None):
        """shows your trophy (longest fish caught)\ncan also view another users trophy, for example: !trophy @Fishy.py"""
        if user is None:
            user = ctx.author
        playeruser = await self.bot.get_player(user)
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
        """users with the highest statistics"""
        await ctx.send_in_codeblock(f"please specify: {ctx.prefix}top ({','.join([c.name for c in ctx.command.commands])})")
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["rods","r"])
    async def rod(self, ctx):
        """shows users with the highest rod levels"""
        playeruser = await self.bot.get_player(ctx.author)
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
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY rodlevel DESC) AS rodlevel FROM f_users) a WHERE userid = ?;",(playeruser.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["nets","n"])
    async def net(self, ctx):
        """shows users with the highest net levels"""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        lvl = playeruser.net_level
        cur = await self.bot.db.execute("SELECT * FROM f_users ORDER BY netlevel DESC")
        topusers = await cur.fetchmany(10)
        step = 1
        table = ""
        for r in topusers:
            player = await self.bot.get_player(r[0])
            player_net = await player.get_net()
            table = table + f"{step}. {player.name} : {player_net.name} (lvl {player_net.level})\n"
            step += 1
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY netlevel DESC) AS netlevel FROM f_users) a WHERE userid = ?;",(playeruser.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["coins","c"])
    async def coin(self, ctx):
        """shows users with the most coins"""
        playeruser = await self.bot.get_player(ctx.author)
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
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY coins DESC) AS coins FROM f_users) a WHERE userid = ?;",(playeruser.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(name='collection', aliases=["collections","cl"])
    async def _collection(self, ctx):
        """shows users with the most fishes in their collections"""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        async with ctx.channel.typing():
            step = 1
            table = ""
            c = await self.bot.db.execute("SELECT userid, COUNT(*) FROM f_collections GROUP BY userid")
            topusers = await c.fetchall()
            sortedtopusers = sorted(topusers, key = lambda x: x[1], reverse=True)
            c = await self.bot.db.execute("SELECT COUNT(*) FROM fishes")
            num_of_fish = await c.fetchone()
            for r in sortedtopusers:
                player = await self.bot.get_player(r[0])
                table = table + f"{step}. {player.name} : {r[1]}/{num_of_fish[0]})\n"
                step += 1
                if step == 10: break
            pos = 1
            for r in sortedtopusers:
                if r[0] == playeruser.id:
                    break
                else:
                    pos += 1
            table = table + f"(your rank: #{pos})"
            await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    @commands.cooldown(1, 10, BucketType.user)
    @top.command(aliases=["totalcaught","tc"])
    async def caught(self, ctx):
        """shows users with the most caught fish"""
        playeruser = await self.bot.get_player(ctx.author)
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
        c = await self.bot.db.execute("SELECT * FROM (SELECT userid, RANK() OVER (ORDER BY totalcaught DESC) AS totalcaught FROM f_users) a WHERE userid = ?;",(playeruser.id,)) # i love this statement
        player_pos = (await c.fetchone())[1]
        table = table + f"(your rank: #{player_pos})"
        await self.bot.db.commit()
        await ctx.send_in_codeblock(table, language='css')
    
    
    @commands.cooldown(1, 60, BucketType.user)
    @commands.command(description="view all fish in your collection with an interactive menu")
    async def collection(self, ctx):
        """allows you to view your collection in an interactive reaction-powered embed"""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        c = await self.bot.db.execute("SELECT oid FROM f_collections WHERE userid = ?", (ctx.author.id,))
        data = await c.fetchall()
        pages = menus.MenuPages(source=botmenus.CollectionSource(data), clear_reactions_after=True)
        await pages.start(ctx)

    ## WIP ##
    # @commands.cooldown(1, 10, BucketType.user)
    # @commands.command(name="rod", description="changes your rod level")
    # async def _rod(self, ctx, new_rod_lvl: int):
    #     """changes your rod to any level that you've previously bought."""
    #     playeruser = await self.bot.get_player(ctx.author)
    #     if playeruser is None:
    #         return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
    #     playerrod = await playeruser.get_rod()
    #     maxlevel = playerrod.level
    #     if new_rod_lvl > maxlevel:
    #         return await ctx.send_in_codeblock(f"sorry, you can't set your rod level above {maxlevel} ({playerrod.name})")
        
    #     await self.bot.db.execute("UPDATE f_users SET rodlevel = ? WHERE userid = ?",(new_rod_lvl, ctx.author.id,))
    #     await self.bot.db.commit()
    #     return await ctx.send_in_codeblock(f"done! your rod is now the {playerrod.name} ({playeruser.rod_level})")

        
            
def setup(bot):
    bot.add_cog(playermeta(bot))
