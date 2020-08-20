import discord
from discord.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def change_prefix(self, ctx, new_prefix):
        f = open("prefixes", "r")
        prefixes = f.read().split("\n")
        for i in range(len(prefixes)):
            if prefixes[i][:prefixes[i].index(":")] == str(ctx.guild.id):
                prefixes[i] == f"{ctx.guild.id}:{new_prefix}"



def setup(bot):
    bot.add_cog(Cog(bot))