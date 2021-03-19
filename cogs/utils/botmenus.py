from discord.ext import menus
import discord

class SQLSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entry):
        embed = discord.Embed(description=f"```css\n{entry}\n```",color=discord.Color.random())
        return embed
    
class CollectionSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entry):
        bot = menu.cxt.bot
        fish = bot.get_fish(entry)
        embed = discord.Embed()
        return embed
