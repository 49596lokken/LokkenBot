import discord
from discord.ext import commands
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.xo_channels = {}


    def get_channel(self, ctx):
        if ctx.guild:
            return(f"{ctx.guild.id} {ctx.channel.id}")
        return(None)
    
    @commands.group(pass_context=True,invoke_without_command=True)
    async def xo(self, ctx):
        ...

    @xo.command(description="Starts a noughts and crosses with a specified person", brief="author of message starts", name="start")
    async def start(self, ctx, opponent: commands.MemberConverter, wager=0):
        wager = int(wager)
        if not ctx.guild:
            await ctx.send("This can only happen in a server")
            return
        if not opponent in ctx.guild.members:
            await ctx.send("Person is not in the server")
        channel = self.get_channel(ctx)
        new_game = XoGame([ctx.author.id, opponent.id], wager)
        if channel in self.xo_channels:
            xo_channel = self.xo_channels[channel]
            for game in xo_channel:
                if ctx.author.id in game.players or opponent.id in game.players:
                    await ctx.send("One of you is already playing in this channel")
                    return
            xo_channel.append(new_game)
        else:
            self.xo_channels[channel] = [new_game]
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
        await ctx.send(new_game.get_board())

    @xo.command(description="Plays in a game of noughts and crosses", name="play")
    async def xo_play(self, ctx, place):
        if not ctx.guild:
            await ctx.send("This can only happen in a server")
            return
        channel = self.get_channel(ctx)
        if not channel in self.xo_channels:
            await ctx.send("No games of noughts and crosses here")   
            return
        playing = False
        for game in self.xo_channels[channel]:
            if ctx.author.id in game.players:
                playing = True
                break
        if not playing:
            await ctx.send("Sorry, you are not in a game here")
            return
        turns_taken = 0
        for tile in game.board:
            if not tile.isdigit():
                turns_taken += 1
        
        if not (game.players.index(ctx.author.id) == turns_taken%2):
            await ctx.send("Wait yor turn")
            return
        
        if not (place in game.board and place.isdigit()):
            await ctx.send(f"\"{place}\" isn't a valid place")
            return
        game.board[game.board.index(place)] = ["X", "O"][game.players.index(ctx.author.id)]
        await ctx.send(game.get_board())
        if game.check_win():
            await ctx.send(f"Well done {ctx.author.mention} you won!")
            if game.wager != 0:
                await ctx.send(f"{ctx.author.display_name} just won {game.wager*2} coins from the wager!")
                lokkoin = await self.bot.get_cog("lokkoin")
                await lokkoin.add_coins(str(ctx.author.id), game.wager*2)
            if len(self.xo_channels[channel]) == 1:
                del self.xo_channels[channel]
                return
            else:
                self.xo_channels[channel].remove(game)
                return
        if turns_taken == 8:
            lokkoin = await self.bot.get_cog("lokkoin")
            await ctx.send("It's a draw. Refunding wager")
            for player in game.players:
                await lokkoin.add_coins(str(player), game.wager)
            if len(self.xo_channels[channel]) == 1:
                del self.xo_channels[channel]
                return
            else:
                self.xo_channels[channel].remove(game)
                return

class XoGame:
    def __init__(self, players, wager):
        self.players=players
        self.board=[str(i+1) for i in range(9)]
        self.wager = wager
    
    def check_win(self):
        if self.board[6] == self.board[4] == self.board[2]:
            return(True)
        if self.board[8] == self.board[4] == self.board[0]:
            return(True)
        if self.board[6] == self.board[3] == self.board[0]:
            return(True)
        if self.board[7] == self.board[4] == self.board[1]:
            return(True)
        if self.board[8] == self.board[5] == self.board[2]:
            return(True)
        if self.board[6] == self.board[7] == self.board[8]:
            return(True)
        if self.board[3] == self.board[4] == self.board[5]:
            return(True)
        if self.board[0] == self.board[1] == self.board[2]:
            return(True)
        return(False)

    def check_over(self):
        for row in self.board:
            for tile in row:
                if not tile:
                    return(False)
        return(True)

    def get_board(self):
        output = ""
        for i in range(9):
            output += self.board[i]
            if i % 3 == 2:
                output += "\n"
            else:
                output += " | "
        return(output)

def setup(bot):
    bot.add_cog(Games(bot))