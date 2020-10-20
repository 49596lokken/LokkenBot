import discord
from discord.ext import commands
import random
import asyncio


class PrimeGame(commands.Cog, name="games"):
    def __init__(self, bot):
        self.bot=bot
        self.primes = [2,3]
        f=open("data/games/prime/channels", "r")
        self.channels = f.read().split("\n")[:-1]
        f.close()
        self.reward = 50

    

    async def gen_next_prime(self):
        test = self.primes[-1]+2
        while True:
            for i in self.primes:
                if test%i==0:
                    p=False
                    break
                if i**2>test:
                    p=True
                    break
            if p:
                self.primes.append(test)
                return
            test += 2

    async def is_prime(self,number):
        if number in self.primes:
            return(True)
        while self.primes[-1]**2 < number:
            await self.gen_next_prime()
        for i in self.primes:
            if i**2 > number:
                return(True)
            if number%i==0:
                return(False)

    @commands.guild_only()
    @commands.group(description="It's a prime number game. Will spam channels so certain permissions are required.\n\nThe object of the game is to send prime numbers to the chat without repeating until someone cannot or repeats. The game will not allow prime numbers over 1 000 000",invoke_without_command=True,pass_context=True)
    async def prime(self,ctx):
        ...
    
    
    @prime.command(description="Registers a channel for a prime number game")
    @commands.has_permissions(manage_channels=True)
    async def register(self,ctx):
        if str(ctx.channel.id) in self.channels:
            return(await ctx.send("This is already a prime number game channel"))
        self.channels.append(str(ctx.channel.id))
        f=open("data/games/prime/channels", "a")
        f.write(str(ctx.channel.id)+"\n")
        f.close()
        await ctx.send("Registered")
    
    @prime.command(description="Unregisters a channel for the prime number game")
    @commands.has_permissions(manage_channels=True)
    async def unregister(self,ctx):
        if not str(ctx.channel.id) in self.channels:
            return(await ctx.send(f"This is not a prime number game channel."))
        f = open("data/games/prime/channels", "r")
        t = f.read().replace(str(ctx.channel.id)+"\n", "")
        f.close()
        f = open("data/games/prime/channels", "w+")
        f.write(t)
        f.close()
        self.channels.remove(str(ctx.channel.id))
        await ctx.send("Unregistered. Sorry to see you go")
    
    @prime.command(description="Starts a round of the prime number game with specified players")
    async def start(self,ctx,*players: commands.MemberConverter):
        if not str(ctx.channel.id) in self.channels:
            return(await ctx.send(f"This is not a prime number game channel. You need to register it with \"{ctx.prefix}prime register\""))
        players = [i for i in players]
        if not ctx.author in players:
            players.append(ctx.author)
        random.shuffle(players)
        if len(players) < 2:
            await ctx.send("Not enough players")
            return
        playing = True
        playernum = 0
        already_had = []
        while playing:
            lost = False
            player = players[playernum]
            await ctx.send(f"{player.mention} It's your turn!\nSend a prime number under 1000000 within 5 seconds or you lose!")
            def check(m):
                return(m.author.id == player.id and m.channel.id == ctx.channel.id and m.content.isdigit())
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=5)
                if int(msg.content) >= 1000000:
                    await ctx.send(f"Sorry {msg.author.mention} That number is too big so you are now out of the game")
                    lost = True
                elif not await self.is_prime(int(msg.content)):
                    await ctx.send(f"Sorry {player.mention}, The number {msg.content} is not prime so you are now out of the game")
                    lost = True
                elif int(msg.content) in already_had:
                    await ctx.send(f"Sorry {player.mention}, The number {msg.content} has already been used so you are now out of the game")
                    lost = True
            except asyncio.TimeoutError:
                await ctx.send(f"Sorry {player.mention}, You took too long and are now out of the game")
                lost = True
            if lost:
                next_player = players[(playernum+1)%len(players)]
                players.remove(player)
                playernum = players.index(next_player)-1
                if len(players) == 1:
                    await ctx.send(f"{next_player.mention} Wins! Well done!")
                    lokkoin = self.bot.get_cog("lokkoin")
                    if lokkoin:
                        await lokkoin.add_coins(str(next_player.id), self.reward)
                        await ctx.send(f"Well done {next_player.display_name}, you won {self.reward} lokkoins!")
                    playing = False
            else:
                already_had.append(int(msg.content))
            playernum += 1
            playernum %= len(players)





def setup(bot):
    bot.add_cog(PrimeGame(bot))