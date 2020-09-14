import discord
from discord.ext import commands
from checks import *
import sys
import subprocess


class Lokken(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
            if not output:
                await ctx.send("You need to specify a commit name!")
                return
            subprocess.run(["git", "add", "./"])
            subprocess.run(["git", "commit", "-m", f"{output}"])
            subprocess.run(["git", "push", "-u", "origin", "master"])
            await ctx.send("Done!")
        else:
            subprocess.run(["sudo", "git", "pull", "-f", "origin", "master"])
            await ctx.send("Done!")
            for extension in self.bot.extensions:
                self.bot.reload_extension(extension)
    

    @commands.command(description="Sends a message in either a guild or DM")
    @is_creator()
    async def send(self, ctx, place, *args):
        args = [arg for arg in args]
        if place.lower() == "dm":
            user = await commands.MemberConverter().convert(ctx,args[0])
            if user:
                output = ""
                for arg in args[1:]:
                    output += arg+" "
                await user.send(output)
        elif place.lower() == "guild":
            args = [arg for arg in args]
            guild = args[0]
            if not guild.isdigit():
                await ctx.send("Not an integer")
                return
            channel = args[1]
            if not channel.isdigit():
                await ctx.send("Not a channel")
                return
            guild = self.bot.get_guild(int(guild))
            if guild:
                channel = guild.get_channel(int(channel))
                if channel:
                    output = ""
                    for arg in args[2:]:
                        output += arg+" "
                    await channel.send(output)
        

            


def setup(bot):
    bot.add_cog(Lokken(bot))
