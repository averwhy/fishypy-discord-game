import discord
import platform
import time
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import aiosqlite
OWNER_ID = 267410788996743168

class meta(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_socket_raw_send(self,payload):
        self.bot.socket_sent_counter += 1
            
    @commands.Cog.listener()
    async def on_socket_raw_receive(self,payload):
        self.bot.socket_recieved_counter += 1
    
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @commands.command(name='prefix',aliases=["pre"],description="changing bot prefix for server(admins only)")
    async def set_prefix(self, ctx, prefix):
        if len(prefix) > 10:
            return await ctx.send_in_codeblock('Prefix is too long')
        self.bot.prefixes[ctx.guild.id] = prefix
        await self.bot.db.execute("UPDATE f_prefixes SET prefix = ? WHERE guildid = ?",(prefix, ctx.guild.id,))
        await self.bot.db.commit()
        return await ctx.send_in_codeblock(f"Prefix updated to {prefix}")
    
    @set_prefix.error
    async def on_prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send_in_codeblock("You must have Manage Guild permissions for this")
        
    @commands.command(description="views bot's news/updates")
    async def news(self,ctx, *,setnews = None): # for this, the news is a botvar so it doesnt get boned on cog reload
        if ctx.author.id == OWNER_ID and setnews is not None:
            self.bot.newstext = setnews
            self.bot.news_set_by = f"[Developer] {ctx.author.name}"
            await ctx.message.add_reaction("\U00002705")
            await ctx.send_in_codeblock("News was set succesfully!")
            return
        embed = discord.Embed(title="Fishy.py News",description=self.bot.newstext,colour=discord.Colour.random())
        embed.set_footer(text=f"News set by {self.bot.news_set_by}")
        await ctx.send(embed=embed)
            
    @commands.cooldown(1,15,BucketType.user)
    @commands.command(description="info and stats about bot", aliases=['ping','information'])
    async def info(self,ctx): # info thing
        # get API ping
        start = time.perf_counter()
        message = await ctx.send_in_codeblock("Getting info...", language='css')
        end = time.perf_counter()
        #now lets get uptime and fancy it
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        #now for database ping, which also doubles as the amount of fish
        start2 = time.perf_counter()
        c = await self.bot.db.execute("SELECT COUNT(*) FROM fishes")
        fishtotal = (await c.fetchone())[0]
        await self.bot.db.commit()
        c = await self.bot.db.execute("SELECT * FROM f_stats")
        totalfished, totalcoinsearned, totalrodsbought = await c.fetchone()
        end2 = time.perf_counter()
        
        duration = round(((end - start) * 1000),1)
        db_duration = round(((end2 - start2) * 1000),1)
        ws = round((self.bot.latency * 1000),2)
        msg = f"""```prolog
Python, Discordpy Version: {platform.python_version()}, {discord.__version__}
Fishes: {fishtotal}
Rods: 539
Total Rods Bought: {totalrodsbought}
Fish Caught Since Start: {self.bot.fishCaughtinsession}
Total Fish Caught: {totalfished}
Total Coins Earned: {totalcoinsearned}
Websocket Ping: {ws}ms
API Ping: {duration}ms
Database Ping: {db_duration}ms
Uptime: {days}d, {hours}h, {minutes}m, {seconds}s
Source: 'https://github.com/averwhy/fishy-discord-game'```
        """
        await message.edit(content=msg)
    
    # @commands.command()
    # async def ping(self, ctx):
    #     em = discord.PartialEmoji(name="loading",animated=True,id=782995523404562432)
    #     start = time.perf_counter()
    #     message = await ctx.send_in_codeblock("Ping...", language='css')
    #     end = time.perf_counter()
    #     start2 = time.perf_counter()
    #     await self.bot.db.commit()
    #     end2 = time.perf_counter()
    #     duration = round(((end - start) * 1000),1)
    #     db_duration = round(((end2 - start2) * 1000),1)
    #     ws = round((self.bot.latency * 1000),1)
    #     await message.edit(content=f"```prolog\nWebsocket.......... {round(self.bot.latency * 1000,2)}ms\nAPI.......... {duration}ms\nDatabase.......... {db_duration}ms\n```")
        
    @commands.cooldown(1,40,BucketType.channel)
    @commands.command()
    async def about(self,ctx):
        embed = discord.Embed(title=f"**About Fishy.py**", description="", colour=discord.Colour(0x158b94))
        embed.set_author(name=f"Developed by @averwhy#3899, Original by @Deda#9999")
        embed.set_footer(text=f"Made with Python {platform.python_version()}",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
        embed.add_field(name="What is Fishy.py?", value="Fishy.py is a fishing style game where you compete with other users or even guilds to have the best collection, or highest level, or fish. Originally created by Deda#9999 and written in JavaScript, Fishy was a huge success and is in over 1,000 servers. Sadly, it went offline as Deda could not host it anymore. But I (averwhy#3899) have recreated it, now better than ever!")
        embed.add_field(name="How does it work?", value="Fishy.py has a database with more than 16,000 fishes, thanks to https://www.fishbase.org ! All of them have unique images and names. When you fish, one is randomly selected from the database. However, in the future [v2], when you have a higher level you have a higher probability of catching more rare and uncommon fish!\nIn terms of technicality, Fishy.py is made with the `discord.py` API, which is a wrapper for the Discord API. Fishy.py also using `aiosqlite` for the database.")
        embed.add_field(name="Have more questions? Feel free to join the support server and ask averwhy#3899!", value=f"The servers invite can be obtained via the `{ctx.prefix}support` command.",inline=False)
        await ctx.send(embed=embed)
    
    @commands.cooldown(1,60,BucketType.guild)
    @commands.command()
    async def support(self,ctx): # this sends the fishypy support server link
        em = discord.Embed(title="Click me for the support server",url="http://discord.gg/HSqevex",color=discord.Color.blue())
        await ctx.send(embed=em)
        
    @commands.command(description="")
    async def invite(self, ctx):
        embed = discord.Embed(description="[discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot](https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot)",color=discord.Color(0x2F3136))
        try: return await ctx.send(embed=embed)
        except discord.Forbidden:
            return await ctx.send("<https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot>")
            
def setup(bot):
    bot.add_cog(meta(bot))
