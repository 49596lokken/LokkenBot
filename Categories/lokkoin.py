import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import random
import typing
import datetime

class lokkoin(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        f = open("data/lokkoin/balances", "r")
        self.balances = {i[:i.index(" ")]:int(i[i.index(" "):-1]) for i in f}
        f.close()
        self.slot_emojis = ["\U0001F514", "\U0001F349", "\U0001F340", "\U0001F352", "\U0001F451", "\U0001F34B", "\U0001F48E"]
        self.claimed_today = []
        self.new_day = None
        coro = self.new_daily_coins()
        asyncio.ensure_future(coro)
        self.daily_loop.start()
        self.awards = []
        self.slots.description=None
        coro = self.update_slots()
        asyncio.ensure_future(coro)


    def cog_unload(self):
        self.daily_loop.cancel()

    async def update_slots(self):
        awards = await self.bot.get_channel(768130720807124992).fetch_message(768131100995354645)
        self.awards = []
        if not awards:
            raise(discord.errors.NotFound)
        for line in awards.content.split("\n"):
            self.awards.append(int(line))
        self.slots.description=f"spins a slot machine\nIf you get a double match (any 2 the same) your bet is multiplied by {self.awards[0]}, unless the mathcing emojis are {self.slot_emojis[-1]} in which case your bet is multiplied by {self.awards[1]}.\nIf you get all 3 the same, your bet is multiplied by {self.awards[2]} unless all 3 are {self.slot_emojis[-1]} in which case the bet is multiplied by {self.awards[3]}"
    
    @tasks.loop(hours=24.0)
    async def daily_loop(self):
        await self.new_daily_coins()
    
    async def new_daily_coins(self):
        self.new_day = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        self.claimed_today = []
    

    async def get_balance(self, user):
        if user in self.balances:
            return(self.balances[user])
        f = open("data/lokkoin/balances", "a")
        f.write(f"{user} 200\n")
        self.balances[user] = 200
        
        return(200)

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

    @commands.command(description="Sends the balance of a player (default is the author)")
    async def balance(self,ctx, player: typing.Optional[commands.MemberConverter]):
        if not player:
            player = ctx.author
        amount = await self.get_balance(str(player.id))
        if amount == None:
            await ctx.send("You need to register with the \"register\" command")
            return
        await ctx.send(f"The balance of {player.name} is: {amount}")
    
    @commands.command(description="Gives you your daily salary")
    async def daily(self, ctx):
        if ctx.author in self.claimed_today:
            await ctx.send(f"You have already claimed today\nYou can claim in {self.new_day-datetime.datetime.utcnow()}")
            return
        self.claimed_today.append(ctx.author)
        await self.add_coins(str(ctx.author.id), 50)
        await ctx.send("Added your 50 daily coins")



    @commands.command(description="Pays a person a set number of lokkoins")
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
    
    @commands.command()
    async def slots(self, ctx, gamble:int=50):
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
            if results[0] == self.slot_emojis[-1]:
                await ctx.send("MEGA WIN!")
                await self.add_coins(str(ctx.author.id), self.awards[3]*gamble)
                return
            await ctx.send("HUGE WIN!")
            await self.add_coins(str(ctx.author.id), self.awards[2]*gamble)
            return
        if results[0] == results[1]:
            if results[0] == self.slot_emojis[-1]:
                await ctx.send("BIG WIN!")
                await self.add_coins(str(ctx.author.id), self.awards[1]*gamble)
                return
            await ctx.send("normal win")
            await self.add_coins(str(ctx.author.id), self.awards[0]*gamble)
            return
        if results[0] == results[2]:
            if results[0] == self.slot_emojis[-1]:
                await ctx.send("BIG WIN!")
                await self.add_coins(str(ctx.author.id), self.awards[1]*gamble)
                return
            await ctx.send("normal win")
            await self.add_coins(str(ctx.author.id), self.awards[0]*gamble)
            return
        if results[2] == results[1]:
            if results[2] == self.slot_emojis[-1]:
                await ctx.send("BIG WIN!")
                await self.add_coins(str(ctx.author.id), self.awards[1]*gamble)
                return
            await ctx.send("normal win")
            await self.add_coins(str(ctx.author.id), self.awards[0]*gamble)
            return
        await ctx.send("Sorry, you lost...")



    


    



def setup(bot):
    
    bot.add_cog(lokkoin(bot))
