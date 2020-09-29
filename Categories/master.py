import discord
from discord.ext import commands
import asyncio
import random
import typing

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.pieces = ["\U0001F534", "\U0001F7E2", "\U0001F535", "\U0001F7E1", "\U0001F7E3", "\U000026AA"]
        self.codes = ["r", "g", "b", "y", "p", "w"]
        self.indicators = ["\u25AA", "\u25AB"]
        temp = [f"{self.pieces[i]} ({self.codes[i]})\n" for i in range(len(self.pieces))]
        self.valid_pieces = ""
        for line in temp:
            self.valid_pieces += line

    @commands.group(pass_context=True,invoke_without_command=True, description="Command group for mastermind games")
    async def master(self,ctx):
        ...
    
    def validate_piece(self, piece):
        if piece in self.codes:
            piece = self.pieces[self.codes.index(piece)]
        if piece in self.pieces:
            return(piece)
        else:
            raise(InvalidPiece)

    @master.command(description="Starts a game of mastermind against the specified opponent (can play against the bot)")
    async def start(self, ctx, opponent: typing.Optional[commands.MemberConverter]):
        if (not opponent) or (opponent.id == self.bot.user.id) :
            opponent = ctx.author
            await ctx.send("Playing against me!")
            code = [random.choice(self.pieces) for i in range(4)]
        else:
            await ctx.author.send(f"As you started the game, you get to make the code. Please enter the code without any spaces or extra characters. You are allowed to use:\n{self.valid_pieces}")
            def check(message):
                if message.channel != ctx.channel or message.author != ctx.author:
                    return(False)
                if len(message.content) != 4:
                    return False
                message.content = [i for i in message.content]
                try:
                    for i in range(len(message.content)):
                        message.content[i]=self.validate_piece(message.content[i])
                    return(True)
                except InvalidPiece:
                    return(False)
            try:
                code = [i for i in (await self.bot.wait_for("message", check=check, timeout=60.0)).content]
            except asyncio.TimeoutError:
                await ctx.send("You waited too long. Game cancelled")
                return
        await ctx.send("Game started\nGuess away!")
        def check1(message):
            if message.channel != ctx.channel or message.author.id != opponent.id:
                return(False)
            if len(message.content) != 4:
                return False
            message.content = [i for i in message.content]
            try:
                for i in range(len(message.content)):
                    message.content[i]=self.validate_piece(message.content[i])
                return(True)
            except InvalidPiece:
                return(False)
        board = ""
        for i in range(10):
            try:
                guess = [char for char in (await self.bot.wait_for("message", check=check1, timeout=30)).content]
            except asyncio.TimeoutError:
                await ctx.send("You took too long guessing\nGame over")
                break
            
            temp_code = code[:]
            blacks = 0
            whites = 0
            for i in range(len(guess)):
                if guess[i] == code[i]:
                    blacks += 1
                if guess[i] in temp_code:
                    temp_code.remove(guess[i])
                    whites += 1
            
            to_send = (whites-blacks)*self.indicators[1]+blacks*self.indicators[0]
            formatted_guess = ""
            for piece in guess:
                formatted_guess += piece
            board = f"{formatted_guess} {to_send}\n" + board
            if to_send == self.indicators[0]*4:
                if opponent == self.bot.user:
                    await ctx.send(f"You beat the computer in {i+1} tries!")
                    lokkoin = self.bot.get_cog("lokkoin")
                    if lokkoin:
                        if await lokkoin.get_balance(str(ctx.author.id)) != None:
                            await lokkoin.add_coins(str(ctx.author.id), 100)
                            await ctx.send("You get 100 lokkoins for beating me!")
                else:
                    await ctx.send(f"You beat {ctx.author.display_name} in {i+1} tries!")
            await ctx.send(board)

        to_send = ""
        for piece in code:
            to_send += piece
        await ctx.send(f"You lose!\n The correct code was {to_send}")
        await ctx.send(board)
            

            


        
    
    @master.command(description="Shows you the valid pieces in a game of mastermind")
    async def valid(self, ctx):
        await ctx.send(self.valid_pieces)


        

    
class InvalidPiece(Exception):
    ...



def setup(bot):
    bot.add_cog(Games(bot))