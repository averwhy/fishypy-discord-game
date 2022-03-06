from cogs.utils import dbc
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
        bot = menu.ctx.bot
        print(entry)
        fish = await bot.get_fish(entry[0])
        splitname = fish.name.split()
        fancy_rarity = await dbc.fish.fancy_rarity(fish.rarity)
        embed = discord.Embed(title=f"{fish.name}",url=f"https://www.fishbase.de/Summary/{splitname[0]}-{splitname[1]}.html", color=fancy_rarity[1])
        embed.set_image(url=fish.image_url)
        embed.add_field(name='__Length__',value=f'{fish.original_length}cm')
        embed.add_field(name='__Rarity__',value=f'{fancy_rarity[0].upper()}')
        embed.set_footer(text=f"Fishy.py Collection Browser | Page {(menu.current_page * self.per_page) + 1}/{self.get_max_pages()}")
        return embed
