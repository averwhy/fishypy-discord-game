from cogs.utils import dbc
from discord.ext import menus
import discord
import logging

log = logging.getLogger(__name__)


class SQLSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entry):
        embed = discord.Embed(
            description=f"```css\n{entry}\n```", color=discord.Color.random()
        )
        return embed


class CollectionSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entry):
        bot = menu.ctx.bot
        print(entry)
        fish = await bot.get_fish(entry[0])
        splitname = fish.name.split()
        fancy_rarity = await dbc.Fish.fancy_rarity(fish.rarity)
        embed = discord.Embed(
            title=f"{fish.name}",
            url=f"https://www.fishbase.de/Summary/{splitname[0]}-{splitname[1]}.html",
            color=fancy_rarity[1],
        )
        embed.set_image(url=fish.image_url)
        embed.add_field(name="__Length__", value=f"{fish.original_length}cm")
        embed.add_field(name="__Rarity__", value=f"{fancy_rarity[0].upper()}")
        embed.set_footer(
            text=f"Fishy.py Collection Browser | Page {(menu.current_page * self.per_page) + 1}/{self.get_max_pages()}"
        )
        return embed


class TrashView(discord.ui.View):
    """Simple class to offer a delete button on welcome messages"""

    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="", emoji="🗑️")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        log.info("Clicked")
        if interaction.channel.permissions_for(interaction.user).manage_messages:
            log.info("Gonna delete")
            await interaction.response.defer()
            try:
                await interaction.message.delete()
            except discord.Forbidden:
                pass  # the bot should have perms to delete its own message, so if this happened, then it's access to the channel was revoked in the timeout frame
        else:
            log.info("Denied")
            await interaction.response.send_message(
                "```sorry, only users with manage messages permissions can click this button.```",
                ephemeral=True,
            )
