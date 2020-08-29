import discord
from discord.ext import commands
from checks import *
import sys


class Lokken(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command()
    @is_creator()
    async def kill(self, ctx):
        await ctx.message.add_reaction("\U0001f44b")
        sys.exit()


def setup(bot):
    bot.add_cog(Lokken(bot))