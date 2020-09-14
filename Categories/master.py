import discord
from discord.ext import commands
import asyncio
import random


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.pieces = ["\U0001F534", "\U0001F7E2", "\U0001F535", "\U0001F7E1", "\U0001F7E3", "\U000026AA"]
        self.codes = ["r", "g", "b", "y", "p", "w"]
        self.indicators = ["\u25AA", "\u25AB"]
        self.games = {}
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
    async def start(self, ctx, opponent: commands.MemberConverter):
        
        await ctx.send("Let's play!")
        if opponent.id == self.bot.user.id:
            if ctx.author in self.games:
                await ctx.send("You are already guessing in a game")
                return
            self.games[ctx.author] = MasterMindGame([random.choice(self.pieces) for i in range(4)], self.bot.user)
            await ctx.send("Playing against me!")
            return
        if opponent in self.games:
            await ctx.send(f"{opponent.display_name} is already in a game!")
            return
        await ctx.author.send(f"As you started the game, you get to make the code. Please enter the code without any spaces or extra characters. You are allowed to use:\n{self.valid_pieces}")
        self.games[opponent] = MasterMindGame(None , ctx.author)
        def check(message):
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
            message = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("You waited too long. Game cancelled")
            return
        self.games[opponent].code = [message.content[i] for i in range(4)]
        await ctx.send("Game started")
    
    @master.command(description="Makes a guess in a game of mastermind. Can either use emojis or the first letter of their colours")
    async def guess(self, ctx, guess):
        if not ctx.author in self.games:
            await ctx.send("You are not currently guessing in a game")
            return
        game = self.games[ctx.author]
        if not game.code:
            await ctx.send("Your opponent hasn't set the code yet")
            return
        if len(guess) != 4:
            await ctx.send(f"You need to use exactly 4 of the following characters:\n{self.valid_pieces}")
            return
        guess = [char for char in guess]
        try:
            for i in range(len(guess)):
                guess[i] = self.validate_piece(guess[i])
        except InvalidPiece:
            await ctx.send(f"Invalid piece. You are only allowed to use:\n{self.valid_pieces}")
            return
        output = []
        temp_code = game.code[:]
        blacks = 0
        whites = 0
        for i in range(len(guess)):
            if guess[i] == game.code[i]:
                output.append(self.indicators[0])
                blacks += 1
            if guess[i] in temp_code:
                temp_code.remove(guess[i])
                output.append(self.indicators[1])
                whites += 1
        
        to_send = (whites-blacks)*self.indicators[1]+blacks*self.indicators[0]
        if len(to_send) == 0:
            await ctx.send("Nothing was correct")
        else:
            await ctx.send(to_send)
        formatted_guess = ""
        for piece in guess:
            formatted_guess += piece
        game.board = f"{formatted_guess} {to_send}\n" + game.board
        game.turns_taken += 1
        if to_send == self.indicators[0]*4:
            if game.opponent == self.bot.user:
                await ctx.send(f"You beat the computer in {game.turns_taken} tries!")
                lokkoin = self.bot.get_cog("lokkoin")
                if lokkoin:
                    if await lokkoin.get_balance(str(ctx.author.id)) != None:
                        await lokkoin.add_coins(str(ctx.author.id), 100)
                        await ctx.send("You get 50 lokkoins for beating me!")
            else:
                await ctx.send(f"You beat {game.opponent.display_name} in {game.turns_taken} tries!")
            del(self.games[ctx.author])
        elif game.turns_taken > 11:
            code = ""
            for piece in game.code:
                code += piece
            await ctx.send(f"You lose!\n The correct code was {code}")
            await ctx.send(game.board)
            del self.games[ctx.author]
    
    @master.command(description="Shows you the board of the game you are guessing in")
    async def board(self, ctx):
        if not ctx.author in self.games:
            await ctx.send("You are not guessing in a game")
            return
        board = self.games[ctx.author].board
        await ctx.send(f"Mastermind game against {self.games[ctx.author].opponent}\n{board}")


        
        

class MasterMindGame:
    def __init__(self, code, opponent):
        self.code = code
        self.turns_taken = 0
        self.opponent = opponent
        self.board = ""
    
class InvalidPiece(Exception):
    ...



def setup(bot):
    bot.add_cog(Games(bot))