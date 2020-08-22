import discord
from discord.ext import commands
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.games = {}


    @commands.group(pass_context=True,invoke_without_command=True)
    async def rng(self,ctx):
        ...
    

    @rng.command()
    async def start(self, ctx, lowest: int=0, highest: int=100):
        if ctx.author in self.games:
            await ctx.send("You are already playing a game!")
            return
        if lowest > highest:
            await ctx.send("Your numbers are the wrong way around")
        await ctx.send(f"I am thinking of a number. It is between {lowest} and {highest}. If you are able to guess my number in under {(highest-lowest)//8} tries, You will get 100 lokkoins")
        self.games[ctx.author] = RngGame(random.randint(lowest, highest), (highest-lowest)//8)

    @rng.command()
    async def guess(self, ctx, guess: int):
        if not ctx.author in self.games:
            await ctx.send("You are not playing now")
            return
        game = self.games[ctx.author]
        if guess < game.number:
            await ctx.send("Too low")
        elif guess > game.number:
            await ctx.send("Too high")
        else:
            await ctx.send("You win!")
            lokkoin = self.bot.get_cog("lokkoin")
            if lokkoin:
                if lokkoin.balance(str(ctx.author.id)) != None:
                    await lokkoin.add_coins(str(ctx.author.id), 100)
                    await ctx.send("You are now 100 lokkoins richer. Spend them wisely")
        

class RngGame:
    def __init__(self, number, tries_for_lokkoins):
        self.number = number
        self.tries_for_lokkoins = tries_for_lokkoins
        self.tries = 0

def setup(bot):
    bot.add_cog(Games(bot))