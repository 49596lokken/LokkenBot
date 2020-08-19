import discord
from discord.ext import commands
import random

class useful(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.alphabet = [chr(i) for i in range(65,91)]
        self.alphabet.append(" ")
        self.all_characters = [chr(i) for i in range(32, 127)]
    
    @commands.command()
    async def print(self, ctx):
        print(ctx.message.content)
    
    @commands.command()
    async def password(self, ctx, length: int):
        pwd = ""
        for i in range(length):
            pwd += random.choice(self.all_characters[1:])
        await ctx.author.send(f"```{pwd}```")
    
    @commands.command()
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
        






def setup(bot):
    bot.add_cog(useful(bot))