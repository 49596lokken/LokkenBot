import discord
from discord.ext import commands


class management(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.brackets = ["()", "{}", "[]", "<>", None]



    @commands.command(aliases=["set_prefix"],description="Changes the prefix for the bot in the server")
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.dm_only())
    async def change_prefix(self, ctx, new_prefix):
        if not ctx.guild:
            f=open("data/prefixes-dm", "r")
            await ctx.send("RIGHT?")
            prefixes = f.read().split("\n")[:-1]
            f.close()
            for i in range(len(prefixes)):
                if prefixes[i][:prefixes[i].index(":")] == str(ctx.author.id):
                    prefixes[i] = f"{ctx.author.id}:{new_prefix}"
                    await ctx.send("Prefix changed")
            output = ""
            f=open("data/prefixes-dm", "w+")
            for user in prefixes:
                output += f"{user}\n"
            f.write(output)
            return
        f = open("data/prefixes", "r")
        prefixes = f.read().split("\n")[:-1]
        f.close()
        for i in range(len(prefixes)):
            if prefixes[i][:prefixes[i].index(":")] == str(ctx.guild.id):
                prefixes[i] = f"{ctx.guild.id}:{new_prefix}"
                await ctx.send("Prefix changed")
        output = ""
        f=open("data/prefixes", "w+")
        for guild in prefixes:
            output += f"{guild}\n"
        f.write(output)
    
    @commands.command(description=f"Changes the bot's nickname to include the prefix in a specified set of brackets in a specified place.")
    @commands.has_permissions(manage_nicknames=True)
    async def update_username(self, ctx, brackets=None, place=None):
        if not ctx.guild:
            await ctx.send("I have no nickname here")
            return
        if not brackets:
            await ctx.send("Resetting username")
            await ctx.guild.me.edit(nick=self.bot.user.name)
        if not brackets in self.brackets:
            await ctx.send(f"Unrecognised brackets\nSuitable brackets are {self.brackets}")
            return
        place=place.lower()
        if not place in ["end", "start"]:
            await ctx.send("Unsuitable place - Please type \"end\" or \"start\"")
            return
        try:
            if place=="end":
                await ctx.guild.me.edit(nick=f"{self.bot.user.name} {brackets[0]}{ctx.prefix}{brackets[1]}")
            else:
                await ctx.guild.me.edit(nick=f"{brackets[0]}{ctx.prefix}{brackets[1]} {self.bot.user.name}")
        except Exception as e:
            await ctx.send(e)


def setup(bot):
    bot.add_cog(management(bot))