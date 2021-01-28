import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168

async def is_owner(ctx):
    return ctx.author.id == OWNER_ID

class funnypicture(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.group(aliases=["fp"], invoke_without_command=True)
    async def funnypicture(self,ctx): # pretend this isnt here
        await ctx.send_in_codeblock(f"Usage: {ctx.prefix}funnypicture [1,2,3,4,5,6]", language='prolog')
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1,30,BucketType.channel)
    @funnypicture.command(aliases=["1"])
    async def one(self,ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/615010360348639243/702892395347312703/unknown.png")
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1,30,BucketType.channel)
    @funnypicture.command(aliases=["2"])
    async def two(self,ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/381963689470984203/778336750036713529/hey.png")
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1,30,BucketType.channel) 
    @funnypicture.command(aliases=["3"])
    async def three(self,ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/381963689470984203/778337440271958018/hey.png")
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1,30,BucketType.channel)
    @funnypicture.command(aliases=["4"])
    async def four(self,ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/381963689470984203/778337541422186538/hey.png")
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1,30,BucketType.channel)
    @funnypicture.command(aliases=["5"])
    async def five(self,ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/381963689470984203/778338556062072892/hey.png")
    
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1,30,BucketType.channel)
    @funnypicture.command(aliases=["6"])
    async def six(self,ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/381963689470984203/778339314089459722/hey.png")

def setup(bot):
    bot.add_cog(funnypicture(bot))