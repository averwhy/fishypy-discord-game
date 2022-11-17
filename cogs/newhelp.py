from typing import Mapping, final
import typing
from discord.ext import commands
from discord.ext.commands import Group
OWNER_ID = 267410788996743168

base_msg = f"""```md
React on message to fish
Compete with others for best collection
#__________COMMANDS__________#
"""
base_msg_command = f"""```md
#__________COMMAND HELP__________#
"""
base_msg_group = f"""```md
#__________COMMAND HELP__________#
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
                    new_msg = new_msg + (f"[{ctx.prefix}{cmd.name} {subcommands.removesuffix('|')}][{cmd.description}]\n")
                else:
                    new_msg = new_msg + (f"[{ctx.prefix}{cmd.name}][{cmd.description}]\n")
        final_msg = new_msg + "\n```"
        await ctx.send(final_msg)

    # This fires once someone does `<prefix>help <cog>`
    async def send_cog_help(self, cog: commands.Cog):
        pass

    # This fires once someone does `<prefix>help <command>`
    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        new_msg = base_msg_command
        new_msg = new_msg + (f"[{ctx.prefix}{command.name}][{command.description}]\n# {command.help}")
        final_msg = new_msg + "\n```"
        await ctx.send(final_msg)

    # This fires once someone does `<prefix>help <group>`
    async def send_group_help(self, group: commands.Group):
        ctx = self.context
        new_msg = base_msg_command
        _ = [f"{sc.name}|" for sc in group.commands]
        final_msg = new_msg + (f"[{ctx.prefix}{group.name}][{group.description}]\n# {group.help}\n")
        for s in group.commands:
            final_msg += f"[{ctx.prefix}{group.name} {s.name}]({s.help})\n"
        
        final_msg += "\n```"
        
        if len(final_msg) > 2000:
            return await ctx.send_in_codeblock(f"unable to send help, message is too big. please annoy my owner to program this in ({ctx.prefix}support)")
        await ctx.send(final_msg)
    
    async def send_error_message(self, error):
        ctx = self.context
        await ctx.send_in_codeblock(str(error).lower().removesuffix('.'))
        
class newhelp(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.bot._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


async def setup(bot):
    await bot.add_cog(newhelp(bot))