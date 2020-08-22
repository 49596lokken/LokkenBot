import discord
from discord.ext import commands


class management(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def change_prefix(self, ctx, new_prefix):
        f = open("prefixes", "r")
        prefixes = f.read().split("\n")[:-1]
        f.close()
        for i in range(len(prefixes)):
            if prefixes[i][:prefixes[i].index(":")] == str(ctx.guild.id):
                prefixes[i] = f"{ctx.guild.id}:{new_prefix}"
                await ctx.send("Prefix changed")
        output = ""
        f=open("prefixes", "w+")
        for guild in prefixes:
            output += f"{guild}\n"
        f.write(output)


def setup(bot):
    bot.add_cog(management(bot))