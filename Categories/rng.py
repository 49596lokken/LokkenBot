import discord
from discord.ext import commands
import random
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.group(pass_context=True,invoke_without_command=True,description="Random number game - I think of a number and you have to guess it in a specified number of tries")
    async def rng(self,ctx):
        ...
    

    @rng.command(description="Starts a game - You can choose the limits")
    async def start(self, ctx, lowest: int=0, highest: int=100):
        if lowest > highest:
            await ctx.send("Your numbers are the wrong way around")
            temp = lowest
            lowest = highest
            highest = temp
        await ctx.send(f"I am thinking of a number. It is between {lowest} and {highest}. If you are able to guess my number in under {int((highest-lowest)**0.5)-1} tries, You will get 100 lokkoins")
        number = random.randint(lowest, highest)
        await ctx.send("Start Guessing!")
        def check(message):
            return(message.author==ctx.author and message.channel==ctx.channel and message.content.isdigit())
        for i in range(int((highest-lowest)**0.5)-1):
            try:
                guess = int((await self.bot.wait_for("message", check=check, timeout=15.0)).content)
            except asyncio.TimeoutError:
                await ctx.send("You took too long!\nGame cancelled!")
                return
            if guess < number:
                await ctx.send("Too low")
            elif guess > number:
                await ctx.send("Too high")
            else:
                await ctx.send("You win!")
                lokkoin = self.bot.get_cog("lokkoin")
                if lokkoin:
                    if await lokkoin.get_balance(str(ctx.author.id)) != None:
                        await lokkoin.add_coins(str(ctx.author.id), 25)
                        await ctx.send("You are now 25 lokkoins richer. Spend them wisely")
                        return
        
        await ctx.send("You lose!")

        
        



def setup(bot):
    bot.add_cog(Games(bot))
