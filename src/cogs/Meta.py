import discord
import platform
import time
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import aiosqlite
OWNER_ID = 267410788996743168

class Meta(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_socket_raw_send(self,payload):
        self.bot.socket_sent_counter += 1
            
    @commands.Cog.listener()
    async def on_socket_raw_receive(self,payload):
        self.bot.socket_recieved_counter += 1
            
    @commands.command()
    async def news(self,ctx, *,setnews = None): # for this, the news is a botvar so it doesnt get boned on cog reload
        if ctx.author.id == OWNER_ID and setnews is not None:
            self.bot.newstext = setnews
            self.bot.news_set_by = str(ctx.author.name)
            await ctx.message.add_reaction("\U00002705")
            await ctx.send("`News was set succesfully!`")
            return
        embed = discord.Embed(title="Fishy.py News",description=self.bot.newstext,colour=discord.Colour.random())
        embed.set_footer(text=f"News set by {self.bot.news_set_by}")
        await ctx.send(embed=embed)
            
    @commands.cooldown(1,15,BucketType.user)
    @commands.command()
    async def info(self,ctx): # info thing
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(title=f"**Info**", description="", colour=discord.Colour(0x158b94))
        embed.set_footer(text=f"Made with Python {platform.python_version()} + enhanced discord.py {discord.__version__}",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
        embed.add_field(name="Uptime", value=f"{days}d, {hours}h, {minutes}m, {seconds}s ago")
        embed.add_field(name="Fish caught since start", value=f"{self.bot.fishCaughtinsession}")
        embed.add_field(name="XP Gained in session",value = f"{round(self.bot.xpgainedinsession,3)}")
        embed.add_field(name="Commands run in session",value=self.bot.commandsRun)
        embed.add_field(name="Command Errors",value=(self.bot.commandsFailed))
        embed.add_field(name="Github link", value="https://github.com/averwhy/fishy-discord-game")
        await ctx.send(embed=embed)
    
    @commands.command()
    async def ping(self, ctx):
        em = discord.PartialEmoji(name="loading",animated=True,id=782995523404562432)
        start = time.perf_counter()
        message = await ctx.send(embed=discord.Embed(title=f"Ping... {em}",color=discord.Color.random()))
        end = time.perf_counter()
        start2 = time.perf_counter()
        async with aiosqlite.connect("fishypy.db")as db:
            await db.commit()
        end2 = time.perf_counter()
        duration = round(((end - start) * 1000),1)
        db_duration = round(((end2 - start2) * 1000),1)
        newembed = discord.Embed(title="Pong!",color=discord.Color.random())
        ws = round((self.bot.latency * 1000),1)
        newembed.add_field(name="Typing",value=f"{duration}ms")
        newembed.add_field(name="Websocket",value=f"{ws}ms")
        newembed.add_field(name="Database",value=f"{db_duration}ms")
        await message.edit(embed=newembed)
        
    @commands.cooldown(1,40,BucketType.channel)
    @commands.command()
    async def about(self,ctx):
        embed = discord.Embed(title=f"**About Fishy.py**", description="", colour=discord.Colour(0x158b94))
        embed.set_author(name=f"Developed by @averwhy#3899, Original by @Deda#9999")
        embed.set_footer(text=f"Made with Python {platform.python_version()}",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
        embed.add_field(name="What is Fishy.py?", value="Fishy.py is a fishing style game where you compete with other users or even guilds to have the best collection, or highest level, or fish. Originally created by Deda#9999 and written in JavaScript, Fishy was a huge success and is in over 1,000 servers. Sadly, it went offline as Deda could not host it anymore. But I (averwhy#3899) have recreated it, now better than ever!")
        embed.add_field(name="How does it work?", value="Fishy.py has a database with more than 16,000 fishes, thanks to https://www.fishbase.org ! All of them have unique images and names. When you fish, one is randomly selected from the database. However, in the future [v2], when you have a higher level you have a higher probability of catching more rare and uncommon fish!\nIn terms of technicality, Fishy.py is made with the `discord.py` API, which is a wrapper for the Discord API. Fishy.py also using `aiosqlite` for the database.")
        embed.add_field(name="Have more questions? Feel free to join the support server and ask averwhy#3899!", value=f"The servers invite can be obtained via the `{self.bot.defaultprefixdefaultprefix}support` command.",inline=False)
        await ctx.send(embed=embed)
    
    @commands.cooldown(1,60,BucketType.guild)
    @commands.command()
    async def support(self,ctx): # this sends the fishypy support server link
        em = discord.Embed(title="Click me for the support server",url="http://discord.gg/HSqevex",color=discord.Color.blue())
        await ctx.send(embed=em)
            
def setup(bot):
    bot.add_cog(Meta(bot))
