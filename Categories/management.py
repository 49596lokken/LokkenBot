import discord
from discord.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command()
    async def change_prefix(self):
        


def setup(bot):
    bot.add_cog(Cog(bot))