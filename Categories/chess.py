import discord
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.black_tiles = {}
        self.white_tiles = {}



    @commands.Cog.listener()
    async def on_ready(self):
        self.white_tiles = {None:"\u2b1b"}
        self.black_tiles = {None:"\u2b1c"}
        for emoji in self.bot.get_guild(721340744207695903):
            if emoji.name.startswith("b"):
                self.black_tiles[emoji.name[1:]] = emoji.emoji
            else:
                self.white_tiles[emoji.name[1:]] = emoji.emoji




def setup(bot):
    bot.add_cog(Games(bot))