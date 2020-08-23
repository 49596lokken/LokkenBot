import discord
from discord.ext import commands


class eh(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.send(exception)

def setup(bot):
    bot.add_cog(
    eh(bot))