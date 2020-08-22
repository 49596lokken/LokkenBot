import discord
from discord.ext import commands
import asyncio


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.c4_channels = {}


    def get_channel(self, ctx):
        if ctx.guild:
            return(f"{ctx.guild.id} {ctx.channel.id}")
        return(None)

    @commands.group(pass_context=True,invoke_without_command=True)
    async def c4(self, ctx):
        ...
    
    @c4.command(name="start")
    async def c4_start(self, ctx, opponent: commands.MemberConverter, wager=0):
        wager = int(wager)
        if not ctx.guild:
            await ctx.send("This can only happen in a server")
            return
        if not opponent in ctx.guild.members:
            await ctx.send("Person is not in the server")
        channel = self.get_channel(ctx)
        new_game = C4Game([ctx.author, opponent], wager)
        if channel in self.c4_channels:
            xo_channel = self.c4_channels[channel]
            for game in xo_channel:
                if ctx.author.id in game.players or opponent.id in game.players:
                    await ctx.send("One of you is already playing in this channel")
                    return
            xo_channel.append(new_game)
        else:
            self.c4_channels[channel] = [new_game]
        if wager != 0:
            confirmation = await ctx.send(f"{opponent.mention}, react to this message with \u2705 within 10 seconds to confirm the wager of {wager} lokkoins")
            await confirmation.add_reaction("\u2705")
            def check(reaction, user):
                return(str(reaction.emoji) == "\u2705" and user == opponent)
            confirmation = await ctx.channel.fetch_message(confirmation.id)
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=10.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Wager cancelled.")
                wager = 0
        if wager != 0:
            lokkoin = self.bot.get_cog("lokkoin")
            if lokkoin:
                balances = [await lokkoin.get_balance(str(ctx.author.id)), await lokkoin.get_balance(str(opponent.id))]
                if balances[0] and balances[1]:
                    if balances[0] > wager and balances[1] > wager:
                        await lokkoin.remove_coins(str(ctx.author.id), wager)
                        await lokkoin.remove_coins(str(opponent.id), wager)
                    else:
                        await ctx.send("One or more of the players have insufficient funds for that")
                else:
                    await ctx.send("one or more of the players aren't registered for lokkoins")
            else:
                await ctx.send("Sorry, lokkoin isn't working right now so you cannot have that wager in this game")
        await ctx.send(f"Game between {ctx.author.mention} and {opponent.mention} started!")
        await ctx.send(f"{new_game.players[new_game.turn%2].mention} It's your turn")
        await ctx.send(new_game.get_board())

    @c4.command(name="play")
    async def c4_play(self, ctx, column: int):
        if not ctx.guild:
            await ctx.send("Please use this command in a guild")
            return
        channel = self.get_channel(ctx)
        if not channel in self.c4_channels:
            await ctx.send("No games of connect 4 here")   
            return
        playing = False
        for game in self.c4_channels[channel]:
            if ctx.author in game.players:
                playing = True
                break
        if not playing:
            await ctx.send("Sorry, you are not in a game here")
            return
        if not ctx.author == game.players[game.turn%2]:
            await ctx.send("It isn't your turn")
            return
        if column > 7 or column < 1:
            await ctx.send("Invalid column")
            return
        try:
            game.play(column, ctx.author)
            game.turn += 1
            if game.check_win():
                await ctx.send(f"{ctx.author.mention} you win!")
                return
            if game.turn == 42:
                await ctx.send("Game was a draw")
            await ctx.send(f"{game.players[game.turn%2].mention} It's your turn")
            await ctx.send(game.get_board())
        except C4Error:
            await ctx.send("Unable to play there")


class C4Game():
    def __init__(self, players, wager):
        self.players = players
        self.tiles = ["\U0001f535", "\U0001F534", "\U0001F7E1"]
        self.board = [[self.tiles[0] for i in range(6)] for i in range(7)]
        self.wager = wager
        self.turn = 0

    def play(self, column: int, player: int):
        column -= 1
        for tile in range(len(self.board[column])-1, -1, -1):
            if self.board[column][tile] == self.tiles[0]:
                self.board[column][tile] = self.tiles[self.players.index(player)+1]
                return
        raise(C4Error)
        
    def get_board(self):
        output = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
        for row in range(6):
            for column in range(7):
                output += self.board[column][row]
            output += "\n"
        return(output)
    
    def check_win(self):
        for column in range(7):
            for row in range(6):
                tile = self.board[column][row]
                if tile != self.tiles[0]:
                    #up left
                    if row > 2 and column > 2:
                        win = True
                        for i in range(1,4):
                            if self.board[column-i][row-i] != tile:
                                win = False
                                break
                        if win:
                            return(True)
                    
                    #up right
                    if row > 2 and column < 4:
                        win = True
                        for i in range(1,4):
                            if self.board[column+i][row-i] != tile:
                                win = False
                                break
                        if win:
                            return(True)
                    
                    #up
                    if row > 2:
                        win = True
                        for i in range(1,4):
                            if self.board[column][row-i] != tile:
                                win = False
                                break
                        if win:
                            return(True)
                    
                    #right
                    if column < 4:
                        win = True
                        for i in range(1,4):
                            if self.board[column+i][row] != tile:
                                win = False
                                break
                        if win:
                            return(True)
        return(False)
                    
class C4Error(Exception):
    ...

def setup(bot):
    bot.add_cog(Games(bot))