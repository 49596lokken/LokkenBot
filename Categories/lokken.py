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
    
    @commands.command()
    @is_creator()
    async def update(self, ctx, commit_name):
        commit_name = commit_name[0]
        if self.bot.user.name == "LokkenTestBot":
            subprocess.run(["git", "add", "./"])
            subprocess.run(["git", "commit", "-m", f"\"{commit_name}\""])
            subprocess.run(["git", "push", "-u", "origin", "master"])

            


def setup(bot):
    bot.add_cog(Lokken(bot))