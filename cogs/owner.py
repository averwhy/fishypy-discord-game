import discord
from discord.ext import commands, tasks
from discord.ext.commands import check
import aiosqlite
import random
from discord.ext import menus
from .utils import botmenus

OWNER_ID = 267410788996743168


class owner(commands.Cog, command_attrs=dict(hidden=True)):
    """
    Tools for the developer
    """

    def __init__(self, bot):
        self.bot = bot
        self.backup_task = self.database_backup_task.start()

    async def cog_check(self, ctx):
        return ctx.author.id == OWNER_ID

    @tasks.loop(minutes=10)
    async def database_backup_task(self):
        try:
            await self.bot.db.commit()
            self.bot.backup_db = await aiosqlite.connect("fpy_backup.db")
            await self.bot.db.backup(self.bot.backup_db)
            await self.bot.backup_db.commit()
            await self.bot.backup_db.close()
            self.bot.last_backup_message = (
                f"The database backed up successfully at {str(discord.utils.utcnow())}"
            )
            return
        except Exception as e:
            self.bot.last_backup_message = f"An error occured while backing up the database at {str(discord.utils.utcnow())}: {e}"
            return

    @commands.group(invoke_without_command=True, hidden=True)
    async def dev(self, ctx):
        # bot dev commands
        await ctx.send_in_codeblock("[Invalid subcommand]", language="css")

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

    @dev.command(aliases=["nick", "n"])
    async def nickname(self, ctx, *, text):
        try:
            await ctx.guild.me.edit(
                nick=text, reason=f"My developer {ctx.author} requested this change"
            )
        except Exception:
            return await ctx.send_in_codeblock("Done", language="css")

    @dev.command(aliases=["logout", "fuckoff", "close", "s"])
    async def stop(self, ctx):
        await ctx.send_in_codeblock("aight, seeya")
        self.bot.fishers.clear()
        await self.bot.db.commit()
        await self.bot.db.close()
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.close()

    @dev.command()
    async def sql(self, ctx, *, statement):
        try:
            cur = await self.bot.db.execute(statement)
            fetchedone = await cur.fetchone()
            fetchedall = await cur.fetchone()
            pages = menus.MenuPages(
                source=botmenus.SQLSource([fetchedone, fetchedall]),
                clear_reactions_after=True,
            )
            await pages.start(ctx)
        except Exception as e:
            return await ctx.send_in_codeblock((f"[{e}]"), language="css")

    @dev.command(aliases=["cu", "c"])
    async def cleanup(self, ctx, amount=20):
        def is_me(m):
            return m.author == self.bot.user

        do_bulk = True
        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            do_bulk = False
        await ctx.send(do_bulk)
        await ctx.channel.purge(limit=amount, check=check, bulk=do_bulk)
        reactions = [
            "✅",
            "<:yesfish:810187479466115102>",
            "<a:snod:798165766888488991>",
        ]
        selected_reaction = (random.choices(reactions, weights=[0.8, 0.1, 0.1], k=1))[0]
        return await ctx.message.add_reaction(selected_reaction)

    @dev.command(hidden=True, name="stream")
    async def streamingstatus(self, ctx, *, name):
        if ctx.author.id != 267410788996743168:
            return
        await self.bot.change_presence(
            activity=discord.Streaming(name=name, url="https://twitch.tv/monstercat/")
        )
        await ctx.send("aight, done")


async def setup(bot):
    await bot.add_cog(owner(bot))
