import discord
from discord.ext import commands
import asyncio
import random
from checks import *

class lokkoin(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        f = open("data/lokkoin/balances", "r")
        self.balances = {i[:i.index(" ")]:int(i[i.index(" "):-1]) for i in f}
        f.close()
        self.slot_emojis = ["\U0001F514", "\U0001F349", "\U0001F340", "\U0001F352", "\U0001F48E", "\U0001F34B"]

    async def get_balance(self, user):
        if user in self.balances:
            return(self.balances[user])
        return(None)

    async def add_coins(self, user, coins: int):
        self.balances[user] += coins
        output = ""
        for user in self.balances:
            output += f"{user} {self.balances[user]}\n"
        f = open("data/lokkoin/balances", "w+")
        f.write(output)
        f.close()

    async def remove_coins(self, user, coins: int):
        self.balances[user] -= coins
        output = ""
        for user in self.balances:
            output += f"{user} {self.balances[user]}\n"
        f = open("data/lokkoin/balances", "w+")
        f.write(output)
        f.close()

    @commands.command()
    async def balance(self,ctx):
        amount = await self.get_balance(str(ctx.author.id))
        if amount == None:
            await ctx.send("You need to register with the \"register\" command")
            return
        await ctx.send(f"Your balance is: {amount}")
    
    @commands.command()
    async def register(self,ctx):
        if str(ctx.author.id) in self.balances:
            await ctx.send("You are already registered")
            return
        f = open("data/lokkoin/balances", "a")
        f.write(f"{ctx.author.id} 200\n")
        self.balances[str(ctx.author.id)] = 200
        await ctx.send("Successfully registered. Your balance is 200 lokkoins!")

    @commands.command()
    async def pay(self, ctx, payee: commands.MemberConverter, amount: int):
        if not str(ctx.author.id) in self.balances:
            await ctx.send("You need to register for lokkoins")
            return
        if not str(payee.id) in self.balances:
            await ctx.send("That person has not registered for lokkoins")
            return
        if amount > await self.get_balance(str(ctx.author.id)):
            await ctx.send("Insufficient funds")
            return
        await self.remove_coins(str(ctx.author.id), amount)
        await self.add_coins(str(payee.id), amount)
        await ctx.author.send(f"Successfully payed {payee.name} {amount} lokkoins!")
        await payee.send(f"{ctx.author.name}#{ctx.author.discriminator} has sent you {amount} lokkoins!")
    
    @commands.command(description="spins a slot machine\nIf you get a double match (any 2 the same) your bet is trippled, unless the mathcing emojis are \U0001F34B in which case your bet is multiplied by 5.\nIf you get all 3 the same, your bet is multiplied by 30 unless all 3 are \U0001F34B in which case the bet is multiplied by 100")
    async def slots(self, ctx, gamble=50):
        if not str(ctx.author.id) in self.balances:
            await ctx.send("In order to gamble, you need to be registered for lokkoins")
            return
        if await self.get_balance(str(ctx.author.id)) < gamble:
            await ctx.send("You do not have the funds for that")
            return
        await self.remove_coins(str(ctx.author.id), gamble)
        msg = await ctx.send("spinning...\n\u2753 | \u2753 | \u2753")
        results = []
        for i in range(3):
            results.append(random.choice(self.slot_emojis))
            await asyncio.sleep(1)
            await msg.edit(content=msg.content.replace("\u2753", results[-1], 1))
        if results[0] == results[1] == results[2]:
            if results[0] == "\U0001F34B":
                await ctx.send("MEGA WIN!")
                await self.add_coins(str(ctx.author.id), 100*gamble)
                return
            await ctx.send("HUGE WIN!")
            await self.add_coins(str(ctx.author.id), 30*gamble)
            return
        if results[0] == results[1]:
            if results[0] == "\U0001F34B":
                await ctx.send("BIG WIN!")
                await self.add_coins(str(ctx.author.id), 5*gamble)
                return
            await ctx.send("normal win")
            await self.add_coins(str(ctx.author.id), 3*gamble)
            return
        if results[0] == results[2]:
            if results[0] == "\U0001F34B":
                await ctx.send("BIG WIN!")
                await self.add_coins(str(ctx.author.id), 5*gamble)
                return
            await ctx.send("normal win")
            await self.add_coins(str(ctx.author.id), 3*gamble)
            return
        if results[2] == results[1]:
            if results[2] == "\U0001F34B":
                await ctx.send("BIG WIN!")
                await self.add_coins(str(ctx.author.id), 5*gamble)
                return
            await ctx.send("normal win")
            await self.add_coins(str(ctx.author.id), 3*gamble)
            return
        await ctx.send("Sorry, you lost...")


    @commands.command()
    @commands.check(is_creator())
    async def set_coins(self, ctx,  player: commands.MemberConverter, coins: int):
        balance = await self.get_balance(str(player.id))
        if balance == None:
            await ctx.send("This player hasn't registered")
            return
        if coins < balance:
            await self.remove_coins(str(player.id), balance-coins)
        elif coins > balance:
            await self.add_coins(str(player.id), coins-balance)
        await ctx.send("Balance updated")

    



def setup(bot):
    bot.add_cog(lokkoin(bot))