import discord
from discord.ext import commands
from checks import *
import sys
import subprocess


class Lokken(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command()
    @is_creator()
    async def kill(self, ctx):
        await ctx.message.add_reaction("\U0001f44b")
        sys.exit()
    
    @commands.command(description="updates the bot")
    @is_creator()
    async def update(self, ctx, *commit_name):
        output = ""
        for word in commit_name:
            output += f"{word} "
        if self.bot.user.name == "LokkenTestBot":
            subprocess.run(["git", "add", "./"])
            subprocess.run(["git", "commit", "-m", f"{output}"])
            subprocess.run(["git", "push", "-u", "origin", "master"])
            await ctx.send("Done!")
        else:
            subprocess.run(["sudo", "git", "pull", "-f", "origin", "master"])
            await ctx.send("Done!")
            for extension in self.bot.extensions:
                self.bot.reload_extension(extension)

            


def setup(bot):
    bot.add_cog(Lokken(bot))
