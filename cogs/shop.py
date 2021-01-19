import platform
import traceback
import asyncio
import time
import os, sys
import aiosqlite
import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check

from .utils import player, server, fish, botchecks

class shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True, name='shop')
    async def _shop(self, ctx):
        pass

    @_shop.command()
    async def rods(self, ctx):
        ...