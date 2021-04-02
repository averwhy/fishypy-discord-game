import discord
import platform
import time
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
from discord.ext.commands import TextChannelConverter
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
    
    @commands.group(invoke_without_command=True, description="changing config for the server (admins only)")
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def config(self, ctx):
        """currently you can do 2 things with this command:\n1. change server prefix. it only affects the server.\n2. blacklist channels. it will prevent the bot from being used in """
        return await ctx.send_in_codeblock(f"please specify, {ctx.prefix}config [prefix/blacklist]")
    
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @config.command(name='prefix',aliases=["pre"],description="changing bot prefix for server(admins only)")
    async def set_prefix(self, ctx, prefix=None):
        """prefix command. allows you to see current prefix, if no prefix is specified. \nprefix can only be changed by users with the Manage Guild permission. (and the bot owner)"""
        if ctx.guild is None:
            return await ctx.send_in_codeblock("prefix cannot be changed in dm's")
        if prefix is None:
            return await ctx.send_in_codeblock(f"current prefix is {self.bot.prefixes[ctx.guild.id]}")
        if len(prefix) > 10:
            return await ctx.send_in_codeblock('Prefix is too long')
        if prefix.strip() == self.bot.defaultprefix:
            cur = await self.bot.db.execute("SELECT * FROM f_prefixes WHERE guildid = ?",(ctx.guild.id,))
            if (await cur.fetchone()) is None:
                await ctx.send_in_codeblock("the prefix is already !")
            self.bot.prefixes.pop(ctx.guild.id)
            await self.bot.db.execute("DELETE FROM f_prefixes WHERE guildid = ?",(ctx.guild.id,))
            await self.bot.db.commit()
            await ctx.send_in_codeblock("prefix reset to default prefix, !")
            return
        self.bot.prefixes[ctx.guild.id] = prefix
        cur = await self.bot.db.execute("SELECT * FROM f_prefixes WHERE guildid = ?",(ctx.guild.id,))
        if (await cur.fetchone()) is None:
            await self.bot.db.execute("INSERT INTO f_prefixes VALUES (?, ?)",(ctx.guild.id, prefix,))
        else:
            await self.bot.db.execute("UPDATE f_prefixes SET prefix = ? WHERE guildid = ?",(prefix, ctx.guild.id,))
        await self.bot.db.commit()
        return await ctx.send_in_codeblock(f"prefix updated to {prefix}")
    
    @set_prefix.error
    async def on_prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send_in_codeblock("you must have Manage Guild permissions to change the servers prefix", language='ml')
        else:
            return await ctx.send_in_codeblock("Internal Error")
    
    @config.command(invoke_without_command=True)
    async def blacklist(self, ctx, channel = None):
        """adds or removes a channel from blacklist, depending on if it is blacklisted or not. channels in the blacklist are completely ignored by the bot (no responses, reactions, etc). this could causes issues if called when users are fishing in it."""
        guilds_channels = [c.id for c in ctx.guild.channels]
        guilds_blacklisted_channels = [c.name for c in ctx.guild.channels if c.id in self.bot.channel_blacklist]
        
        if channel.strip().lower() != "all":
            channel = await TextChannelConverter().convert(ctx, channel)
        
        if not channel: 
            return await ctx.send_in_codeblock(
                f"channels in this server: {len(ctx.guild.channels)}\nblacklisted channels: {len(guilds_blacklisted_channels)} ({', '.join(guilds_blacklisted_channels)})"
                )
        
        elif channel.strip().lower() == "all":
            check_channels = [c.id for c in ctx.guild.channels if c.id in self.bot.channel_blacklist]
            if len(check_channels) == (len(ctx.guild.channels) - 1): # all channels in blacklist for some reason
                for c in check_channels:
                    if c == ctx.channel.id:
                        continue
                    self.bot.channel_blacklist.remove(c)
                    await self.bot.db.execute("INSERT INTO f_blacklist VALUES (?)",(c,))
                await self.bot.db.commit()
                return await ctx.send_in_codeblock(f"removed {len(check_channels)} channels from blacklist")
            for c in ctx.guild.channels:
                if c.id == ctx.channel.id:
                    continue
                self.bot.channel_blacklist.append(c.id)
                await self.bot.db.execute("INSERT INTO f_blacklist VALUES (?)",(c.id,))
            await self.bot.db.commit()
            return await ctx.send_in_codeblock(f"added {len(ctx.guild.channels) - 1} (all) channels to blacklist (except this one)")
        
        elif channel.id in self.bot.channel_blacklist:
            self.bot.channel_blacklist.remove(channel.id)
            await self.bot.db.execute("DELETE FROM f_blacklist WHERE channelid = ?", (channel.id,))
            await self.bot.db.commit()
            return await ctx.send_in_codeblock(f"removed #{str(channel)} from blacklist", language='css')
        
        elif channel.id not in self.bot.channel_blacklist:
            self.bot.channel_blacklist.append(channel.id)
            await self.bot.db.execute("INSERT INTO f_blacklist VALUES (?)", (channel.id,))
            await self.bot.db.commit()
            return await ctx.send_in_codeblock(f"added #{str(channel)} to blacklist", language='css')
        
        else:
            return await ctx.send_in_codeblock(f"something went wrong, please try running the command again, if this persists then please join the support server [ {ctx.prefix}support ]", language='ini')
        
    
    @commands.cooldown(1,15,BucketType.user)
    @commands.command(description="info and stats about bot", aliases=['information','info'])
    async def stats(self,ctx): # info thing
        """shows bot statistics, such as versions, ping (connection to discord), total fish caught, users fishing, etc"""
        #now lets get uptime and fancy it
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        c = await self.bot.db.execute("SELECT COUNT(*) FROM fishes")
        fishtotal = (await c.fetchone())[0]
        c = await self.bot.db.execute("SELECT COUNT(*) FROM f_rods")
        rodtotal = (await c.fetchone())[0]
        c = await self.bot.db.execute("SELECT COUNT(*) FROM f_nets")
        nettotal = (await c.fetchone())[0]
        await self.bot.db.commit()
        c = await self.bot.db.execute("SELECT * FROM f_stats")
        fstats = await c.fetchone()
        totalfished = fstats[0]
        totalcoinsearned = fstats[1]
        totalrodsbought = fstats[2]
        msg = f"""```css
Python, Discordpy Version: {platform.python_version()}, {discord.__version__}
Fishes: {fishtotal}
Rods: {rodtotal}
Nets: {nettotal}
Total Rods Bought: {totalrodsbought}
Fish Caught (Since Start): {self.bot.fishCaughtinsession}
Fish Caught (Total): {totalfished}
Total Coins Earned: {totalcoinsearned}
Users fishing: {len(self.bot.fishers)}
Users autofishing: {len(self.bot.autofishers)}
Uptime: {days}d, {hours}h, {minutes}m, {seconds}s```
        """.lower()
        await ctx.send(content=msg)
        
    @commands.cooldown(1,10,BucketType.user)
    @commands.command(description="shows bots latency to discord", hidden=True)
    async def ping(self, ctx): # info thing
        # get API ping
        start = time.perf_counter()
        message = await ctx.send_in_codeblock("Getting info...", language='css')
        end = time.perf_counter()
        #now for database ping, which also doubles as the amount of fish
        start2 = time.perf_counter()
        await self.bot.db.execute("SELECT * FROM f_rods")
        await self.bot.db.commit()
        end2 = time.perf_counter()
        
        duration = round(((end - start) * 1000),1)
        db_duration = round(((end2 - start2) * 1000),1)
        ws = round((self.bot.latency * 1000),2)
        msg = f"""```css
Websocket Ping: {ws}ms
API Ping: {duration}ms
Database Ping: {db_duration}ms```
        """.lower()
        await message.edit(content=msg)
    
    @commands.cooldown(1,10,BucketType.channel)
    @commands.command(hidden=True)
    async def about(self,ctx):
        embed = discord.Embed(title=f"**About Fishy.py**", description="", colour=discord.Colour(0x158b94))
        embed.set_author(name=f"Developed by @averwhy#3899, Original by @Deda#9999")
        embed.set_footer(text=f"Made with Python {platform.python_version()}",icon_url="https://images-ext-1.discordapp.net/external/0KeQjRAKFJfVMXhBKPc4RBRNxlQSiieQtbSxuPuyfJg/http/i.imgur.com/5BFecvA.png")
        embed.add_field(name="What is Fishy.py?", value="Fishy.py is a fishing style game where you compete with other users or even guilds to have the best collection, or highest level, or fish. Originally created by Deda#9999 and written in JavaScript, Fishy was a huge success and is in over 1,000 servers. Sadly, it went offline as Deda could not host it anymore. But I (averwhy#3899) have recreated it, now better than ever!")
        embed.add_field(name="How does it work?", value="Fishy.py has a database with more than 16,000 fishes, thanks to https://www.fishbase.org ! All of them have unique images and names. When you fish, one is randomly selected from the database. However, in the future [v2], when you have a higher level you have a higher probability of catching more rare and uncommon fish!\nIn terms of technicality, Fishy.py is made with the `discord.py` API, which is a wrapper for the Discord API. Fishy.py also using `aiosqlite` for the database.")
        embed.add_field(name="Have more questions? Feel free to join the support server and ask averwhy#3899!", value=f"The servers invite can be obtained via the `{ctx.prefix}support` command.",inline=False)
        await ctx.send(embed=embed)
    
    @commands.cooldown(1,15,BucketType.guild)
    @commands.command(description='invite to the fishy.py support server')
    async def support(self,ctx): # this sends the fishypy support server link
        em = discord.Embed(title="Click me for the support server",url="http://discord.gg/HSqevex",color=discord.Color.blue())
        await ctx.send(embed=em)
        
    @commands.command(description="invites me to your server")
    async def invite(self, ctx):
        embed = discord.Embed(description="[discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot](https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot)",color=discord.Color(0x2F3136))
        try: return await ctx.send(embed=embed)
        except discord.Forbidden:
            return await ctx.send("<https://discord.com/api/oauth2/authorize?client_id=708428058822180874&permissions=289856&scope=bot>")
            
def setup(bot):
    bot.add_cog(meta(bot))
