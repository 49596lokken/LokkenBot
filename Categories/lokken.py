import discord
from discord.ext import commands
import sys
import subprocess


class Lokken(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot


    async def cog_check(self,ctx):
        return(ctx.author.id == 360493765154045952)

    @commands.command()
    async def kill(self, ctx):
        await ctx.message.add_reaction("\U0001f44b")
        sys.exit()
    
    @commands.command(description="updates the bot")
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


    @commands.command(description="Sets the balance of a person")
    async def set_coins(self, ctx,  player: commands.MemberConverter, coins: int):
        f = open("data/lokkoin/balances", "r")
        to_write = ""
        found = False
        for line in f:
            if line[:line.index(" ")] == str(player.id):
                line = f"{player.id} {coins}\n"
            to_write += line
        f.close()
        if not found:
            to_write += f"{player.id} {coins}\n"
        f = open("data/lokkoin/balances", "w")
        f.write(to_write)
        f.close()

    @commands.command(description="Prints a Line to the console")
    async def print(self, ctx,*, to_print):
        print(to_print)

    @commands.command(description="Reloads a cog")
    async def reload(self,ctx, cog_name):
        self.bot.reload_extension(f"Categories.{cog_name}")
        await ctx.send(f"{cog_name} has been reloaded")


    @commands.command(description="Unloads a Cog")
    async def unload(self,ctx, cog_name):
        self.bot.remove_cog(cog_name)
        self.bot.unload_extension(f"Categories.{cog_name}")
        await ctx.send(f"{cog_name} has been unloaded")


    @commands.command(description="Loads a Cog")
    async def load(self,ctx, cog_name):
        self.bot.load_extension(f"Categories.{cog_name}")
        await ctx.send(f"{cog_name} has been loaded")                
            


def setup(bot):
    bot.add_cog(Lokken(bot))
