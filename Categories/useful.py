import discord
from discord.ext import commands
import random
import datetime
import sys

class useful(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.alphabet = [chr(i) for i in range(65,91)]
        self.alphabet.append(" ")
        self.all_characters = [chr(i) for i in range(32, 127)]

    
    @commands.command(description="encodes a piece of text according to an algorithm. Encoding is the same as decoding")
    async def encode(self, ctx, password, number: int, *message):
        to_encode =""
        for word in message:
            to_encode += word+" "
        output = ""
        target_sum = 0
        for char in password:
            if not char in self.all_characters:
                await ctx.send(f"character: \"{char}\" not supported")
                return
            target_sum += self.all_characters.index(char)
        for char in to_encode:
            target_sum %= len(self.all_characters)
            if not char in self.all_characters:
                await ctx.send(f"character: \"{char}\" not supported")
                return
            new_char = self.all_characters[(target_sum-self.all_characters.index(char)%len(self.all_characters))]
            output += "\\"*int(not new_char.upper())+new_char
            target_sum += number
        if output[0] == " ":
            i = 1
            while output[i] == " ":
                i += 1
            await ctx.send(f"{i} space(s) at the start")
        if output[-1] == " ":
            i = 1
            while output[len(output)-1-i] == " ":
                i += 1
            await ctx.send(f"{i} space(s) at the end")

        await ctx.send(output)
    
    @commands.command(description="sends you an invite to the test server")
    async def test(self, ctx):
        main_channel = self.bot.get_channel(731187247449243658)
        new_invite = await main_channel.create_invite(unique = False)
        await ctx.author.send(f"Please join my test server at \n{new_invite}")
    
    @commands.command(description="Finds the ping in ms")
    async def ping(self, ctx):
        now = datetime.datetime.utcnow()
        await ctx.send(f"The ping is: ```{round((now-ctx.message.created_at).total_seconds()*1000)}ms```")
    
    @commands.command(description="Tells you about the bot")
    async def info(self, ctx):
        version = sys.version[:sys.version.index(" ")]
        f = open("README.md", "r")
        extra_info=f.read()
        f.close()
        extra_info = extra_info[extra_info.index("\n"):]
        if self.bot.user.id!=698859232329596988:
            extra_info = extra_info.replace("698859232329596988", str(self.bot.user.id))
        e = discord.Embed(title=f"{self.bot.user.name} Info" ,description=f"Running on discord.py version: {discord.__version__}\nPython Version: {version}\nCurrently in {len(self.bot.guilds)} different servers\nGithub - [here](https://github.com/49596lokken/LokkenBot){extra_info}")
        await ctx.send(embed=e)





def setup(bot):
    bot.add_cog(useful(bot))
