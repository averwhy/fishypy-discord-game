from typing import Mapping
import typing
import discord
import platform
import time
import random
import asyncio
import re, os
from datetime import datetime
from discord.ext import commands, menus
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import inspect
OWNER_ID = 267410788996743168

# CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL
# oh and also credit to kal
# await kal.credit()

base_msg = f"""```md
React on message to fish
Compete with others for best collection
#__________COMMANDS__________#
"""

class HelpCommand(commands.HelpCommand):
    """Sup averwhy hopefully this is all easy to understand."""

    # This fires once someone does `<prefix>help`
    async def send_bot_help(self, mapping: Mapping[typing.Optional[commands.Cog], typing.List[commands.Command]]):
        ctx = self.context
        new_msg = base_msg
        for cog, cmds in mapping.items():
            cmds = await self.filter_commands(cmds,sort=False)
            for cmd in cmds:
                new_msg = new_msg + (f"[{cmd.name}][{cmd.description}]\n")
        final_msg = new_msg + "\n```"
        await ctx.send(final_msg)

    # This fires once someone does `<prefix>help <cog>`
    async def send_cog_help(self, cog: commands.Cog):
        pass

    # This fires once someone does `<prefix>help <command>`
    async def send_command_help(self, command: commands.Command):
        ctx = self.context

        final_msg = base_msg
        embed = discord.Embed(title=f"{self.clean_prefix}{command.qualified_name} {command.signature}",
                              description=f"{command.help or command.description}")

        await ctx.send(embed=embed)

    # This fires once someone does `<prefix>help <group>`
    async def send_group_help(self, group: commands.Group):
        ctx = self.context

        embed = discord.Embed(title=f"{self.clean_prefix}{group.qualified_name} {group.signature}",
                              description=group.help)
        embed.set_footer(text=f"Do {self.clean_prefix}help [command] for more help")

        for command in group.commands:
            embed.add_field(name=f"{self.clean_prefix}{command.name} {command.signature}",
                            value=command.description,
                            inline=False)

        await ctx.send(embed=embed)
        
class newhelp(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.bot._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(newhelp(bot))