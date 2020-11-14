import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168

async def is_owner(ctx):
    return ctx.author.id == OWNER_ID

class funnypicture(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(aliases=["fp"])
    @commands.check(is_owner)
    async def funnypicture(self,ctx): # pretend this isnt here
        await ctx.send("https://cdn.discordapp.com/attachments/615010360348639243/702892395347312703/unknown.png")

def setup(bot):
    bot.add_cog(funnypicture(bot))