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
from discord.ext.commands import Group
import inspect
OWNER_ID = 267410788996743168

base_msg = f"""```md
React on message to fish
Compete with others for best collection
#__________COMMANDS__________#
"""
base_msg_command = f"""```md
#__________COMMAND_HELP__________#
"""
base_msg_group = f"""```md
Please note: this is a work in progress.
#__________COMMAND_HELP__________#
"""

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={'description': 'shows this message', 'help': 'shows this message. you can also do !help [command] for more info on a command.\nexample: !help fish'})
    # This fires once someone does `<prefix>help`
    async def send_bot_help(self, mapping: Mapping[typing.Optional[commands.Cog], typing.List[commands.Command]]):
        ctx = self.context
        new_msg = base_msg
        for cog, cmds in mapping.items():
            cmds = await self.filter_commands(cmds,sort=False)
            for cmd in cmds:
                if isinstance(cmd, Group):
                    _ = [f"{sc.name}|" for sc in cmd.commands]
                    subcommands = "".join(_)
                    new_msg = new_msg + (f"[{cmd.name} {subcommands.removesuffix('|')}][{cmd.description}]\n")
                else:
                    new_msg = new_msg + (f"[{cmd.name}][{cmd.description}]\n")
        final_msg = new_msg + "\n```"
        await ctx.send(final_msg)

    # This fires once someone does `<prefix>help <cog>`
    async def send_cog_help(self, cog: commands.Cog):
        pass

    # This fires once someone does `<prefix>help <command>`
    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        new_msg = base_msg_command
        new_msg = new_msg + (f"[{command.name}][{command.description}]\n< {command.help} >")
        final_msg = new_msg + "\n```"
        await ctx.send(final_msg)

    # This fires once someone does `<prefix>help <group>`
    async def send_group_help(self, group: commands.Group):
        ctx = self.context
        new_msg = base_msg_command
        _ = [f"{sc.name}|" for sc in group.commands]
        subcommands = "".join(_)
        final_msg = new_msg + (f"[{group.name} ({subcommands.removesuffix('/')})][{group.description}]\n< {group.help} >")
        await ctx.send(final_msg)
        
class newhelp(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.bot._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(newhelp(bot))