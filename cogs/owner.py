import discord
import platform
import time
from discord.ext import commands, tasks, flags
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import asyncio
import aiosqlite
import random
from datetime import datetime
OWNER_ID = 267410788996743168

class owner(commands.Cog, command_attrs=dict(hidden=True)):
    """
    Tools for the developer
    """
    def __init__(self,bot):
        self.bot = bot
        self.dev.add_command(self.sql)
    
    async def cog_check(self,ctx):
        return ctx.author.id == OWNER_ID
        
    @tasks.loop(minutes=30)
    async def database_backup_task(self):
        try:
            await self.bot.db.commit()
            self.bot.backup_db = await aiosqlite.connect('fpy_backup.db')
            await self.bot.db.backup(self.bot.backup_db)
            await self.bot.backup_db.commit()
            await self.bot.backup_db.close()
            return
        except Exception as e:
            print(f"An error occured while backing up the database: {e}")
            return
        
    
    @commands.group(invoke_without_command=True,hidden=True)
    async def dev(self, ctx):
        #bot dev commands
        await ctx.send_in_codeblock("Invalid subcommand", language='css')

    @dev.command(aliases=["r","reloadall"])
    async def reload(self, ctx):
        output = ""
        amount_reloaded = 0
        async with ctx.channel.typing():
            for e in self.bot.initial_extensions:
                try:
                    self.bot.reload_extension(e)
                    amount_reloaded += 1
                except Exception as e:
                    e = str(e)
                    output = output + e + "\n"
            await asyncio.sleep(1)
            if output == "":
                await ctx.send(content=f"`{len(self.bot.initial_extensions)} cogs succesfully reloaded.`") # no output = no error
            else:
                await ctx.send(content=f"`{amount_reloaded} cogs were reloaded, except:` ```\n{output}```") # output

    @dev.command(aliases=["load","l"])
    async def loadall(self, ctx):
        output = ""
        amount_loaded = 0
        async with ctx.channel.typing():
            for e in self.bot.initial_extensions:
                try:
                    self.bot.load_extension(e)
                    amount_loaded += 1
                except Exception as e:
                    e = str(e)
                    output = output + e + "\n"
            await asyncio.sleep(1)
            if output == "":
                await ctx.send(content=f"`{len(self.bot.initial_extensions)} cogs succesfully loaded.`") # no output = no error
            else:
                await ctx.send(content=f"`{amount_loaded} cogs were loaded, except:` ```\n{output}```") # output

    @dev.command()
    async def status(self, ctx, *, text):
        # Setting `Playing ` status
        if text is None:
            await ctx.send(f"{ctx.guild.me.status}")
        if len(text) > 60:
            await ctx.send("`Too long you pepega`")
            return
        try:
            await self.bot.change_presence(activity=discord.Game(name=text))
            await ctx.message.add_reaction("\U00002705")
        except Exception as e:
            await ctx.message.add_reaction("\U0000274c")
            await ctx.send(f"`{e}`")
    
    @dev.command(aliases=['nick','n'])
    async def nickname(self, ctx, *, text):
        try:
            await ctx.guild.me.edit(nick=text, reason=f"My developer {ctx.author} requested this change")
        except:
            return await ctx.send_in_codeblock("Done", language='css')

    @dev.command()
    async def stop(self, ctx):
        await ctx.send_in_codeblock("aight, seeya")
        self.bot.fishers.clear()
        await self.bot.db.commit()
        await self.bot.db.close()
        await self.bot.logout()
        
    @flags.add_flag("--fetchall", action='store_true')
    @flags.add_flag("--fetchone", action='store_true')
    @flags.add_flag("--fetchmany", type=int, default=0)
    @flags.command()
    async def sql(self, ctx, *, statement, **flags):
        try:
            cur = await self.bot.db.execute(statement)
            try:
                do_fetchone = flags['--fetchone']
                do_fetchall = flags['--fetchall']
                do_fetchmany = flags['--fetchmany']
            except KeyError:
                pass
            if do_fetchone:
                result = await cur.fetchone()
                await ctx.send_in_codeblock((f"$ {result}"), language='tex')
            if do_fetchall:
                result = await cur.fetchall()
                await ctx.send_in_codeblock((f"$ {result}"), language='tex')
            if do_fetchmany != 0:
                result = await cur.fetchmany(do_fetchmany)
                await ctx.send_in_codeblock((f"$ {result}"), language='tex')
            else:
                result = await cur.fetchone()
                return await ctx.send_in_codeblock((f"$ {result}"), language='tex')
        except Exception as e:
            return await ctx.send_in_codeblock((f"[{e}]"))
    
    @dev.command(aliases=['cu','c'])
    async def cleanup(self, ctx, amount=100):
        wordlist = ["yoinked","yeeted","throwned","chucked","lobbed","propelled","bit the dust","tossed","are now sleeping with the fishes"] # because funny
        try:
            def is_me(m):
                return m.author == self.bot.user

            deleted = 0
            async for m in ctx.channel.history(limit=amount):
                if is_me(m):
                    await m.delete()
                    deleted += 1
                else:
                    pass
            return await ctx.send_in_codeblock((f"ok, {deleted}/{amount} messages {random.choice(wordlist)}"))
        except Exception as e:
            await ctx.send_in_codeblock(f"hm, didn't work\n[{e}]", language='css')
    
    @dev.command(hidden=True,name="stream")
    async def streamingstatus(self, ctx, *, name):
        if ctx.author.id != 267410788996743168:
            return
        await self.bot.change_presence(activity=discord.Streaming(name=name,url="https://twitch.tv/monstercat/"))
        await ctx.send("aight, done")
        
def setup(bot):
    bot.add_cog(owner(bot))