from discord.ext import commands

class shops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True, description='shows you the prices of upgrades for rods and nets')
    async def shop(self, ctx):
        """the main shop command, here you can see the prices of rods and nets"""
        await ctx.send_in_codeblock(f"usage: {ctx.prefix}shop [rods, nets]")

    @shop.command(aliases=["rod","r"])
    async def rods(self, ctx):
        """shows you your current rod, and the upcoming rods you can buy"""
        playeruser = await self.bot.get_player(ctx.author)
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
        
    @shop.command(aliases=["net","n"])
    async def nets(self, ctx):
        """shows you your current net, and the upcoming nets you can buy"""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        lvl = playeruser.net_level
        cur = await self.bot.db.execute("SELECT * FROM f_nets WHERE level = ?",(playeruser.rod_level,))
        data = await cur.fetchone()
        table = f"#________SHOP NETS________#"
        for r in range(6):
            step = r + lvl
            if step == lvl:
                cur = await self.bot.db.execute("SELECT * FROM f_nets WHERE level = ?",(step,))
                data = await cur.fetchone()
                table = table + f"\n[{data[1]}][{data[2]} coins] *current net*"
            else:
                cur = await self.bot.db.execute("SELECT * FROM f_nets WHERE level = ?",(step,))
                data = await cur.fetchone()
                table = table + f"\n[{data[1]}][{data[2]} coins]"
        
        table = table + f"\n(and more...)({playeruser.coins} coins)"
        await ctx.reply_in_codeblock(table, language='md')
    
    @commands.group(invoke_without_command=True, aliases=["u"], description="buy new rods or nets automatically")
    async def upgrade(self, ctx):
        """buys something"""
        await ctx.send_in_codeblock(f"please specify {ctx.prefix}upgrade [rod/net]")
        
    @upgrade.command(name='rod')
    async def _rod(self, ctx):
        """buys the next avaliable rod automatically, if you have enough coins"""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        cur = await self.bot.db.execute("SELECT * FROM f_rods WHERE level = ?",((playeruser.rod_level + 1),))
        data = await cur.fetchone()
        if data is None:
            return await ctx.reply_in_codeblock('you have the max rod level!', language='css')
        
        if playeruser.coins < data[2]:
            return await ctx.reply_in_codeblock(f'you cannot afford a rod upgrade, you need {round((data[2] - playeruser.coins),2)} more coins')
        
        await self.bot.db.execute("UPDATE f_users SET rodlevel = (rodlevel + 1) WHERE userid = ?",(ctx.author.id,))
        await self.bot.db.execute("UPDATE f_users SET coins = (coins - ?) WHERE userid = ?",(data[2], ctx.author.id,))
        await self.bot.db.commit()
        await ctx.reply_in_codeblock(f"success! new rod: {data[1]}")
    
    @upgrade.command(name='net')
    async def _net(self, ctx):
        """buys the next avaliable net automatically, if you have enough coins"""
        playeruser = await self.bot.get_player(ctx.author)
        if playeruser is None:
            return await ctx.send_in_codeblock(f"you dont have a profile, use {ctx.prefix}start to get one")
        
        cur = await self.bot.db.execute("SELECT * FROM f_nets WHERE level = ?",((playeruser.net_level + 1),))
        data = await cur.fetchone()
        if data is None:
            return await ctx.reply_in_codeblock('you have the max net level!', language='css')
        
        if playeruser.coins < data[2]:
            return await ctx.reply_in_codeblock(f'you cannot afford a net upgrade, you need {round((data[2] - playeruser.coins),2)} more coins')
        
        await self.bot.db.execute("UPDATE f_users SET netlevel = (netlevel + 1) WHERE userid = ?",(ctx.author.id,))
        await self.bot.db.execute("UPDATE f_users SET coins = (coins - ?) WHERE userid = ?",(data[2], ctx.author.id,))
        await self.bot.db.commit()
        await ctx.reply_in_codeblock(f"success! new net: {data[1]}")
        
            
def setup(bot):
    bot.add_cog(shops(bot))
        