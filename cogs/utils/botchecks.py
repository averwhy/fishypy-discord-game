from discord.ext.commands import CheckFailure


class BlacklistedChannel(CheckFailure):
    pass


class FishNotFound(Exception):
    pass


class BanCheckError(CheckFailure):
    pass


async def ban_check(ctx):
    c = await ctx.bot.db.execute(
        "SELECT * FROM f_bans WHERE userid = ?", (ctx.author.id,)
    )
    data = await c.fetchone()
    if data is None:  # If none, user is not banned
        return True
    raise BanCheckError()


class IsNotInGuild(CheckFailure):
    pass


async def is_in_guild(ctx):
    if ctx.guild is None:
        raise IsNotInGuild()
    return True


class AlreadyFishing(Exception):
    pass
