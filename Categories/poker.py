import discord
from discord.ext import commands
import random


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.deck = [[i % 13, i % 4] for i in range(52)]
        self.deck.sort()
        self.suits = ["\u2663", "\u2666", "\u2660", "\u2665"]
        self.numbers = [str(i) for i in range(2, 11)]
        self.numbers.extend(["J", "Q", "K", "A"])
        self.start_message = "Please react to this message with \u270B if you want to play a game of poker with stud size "
        self.lokkoin = self.bot.get_cog("lokkoin")

    def get_card(self, card):
        return(f"{self.numbers[card[0]]}{self.suits[card[1]]}")

    @commands.group(description="Simple poker games in discord channels. Bets are made with Lokkoins. No maximum bet or bot playing\nAlso aces high because I'm lazy", invoke_without_context=True, pass_context=True)
    async def poker(self, ctx):
        ...

    @poker.command(description="Gets a channel ready for poker")
    async def ready(self, ctx, stud_size: int = 5):
        if not ctx.guild:
            await ctx.send("Games cannot be played in dms")
            return
        if ctx.channel in self.games:
            await ctx.send("There's already a game here")
            return
        if stud_size < 5:
            await ctx.send("You need to play with more than 5 cards")
            return
        msg = await ctx.send(f"{self.start_message}{stud_size}")
        await msg.add_reaction("\u270B")
        self.games[ctx.channel] = msg

    @poker.command(description="Starts a game of poker")
    async def start(self, ctx):
        if not ctx.guild:
            await ctx.send("Poker is for servers only!")
            return
        if not ctx.channel in self.games:
            await ctx.send("You need to ready the channel for a game")
            return
        if not self.games[ctx.channel].id:
            await ctx.send("The game in this channel has already started")
            return
        msg = await ctx.fetch_message(self.games[ctx.channel].id)
        for reaction in msg.reactions:
            if reaction.emoji == "\U0000270B":
                players = await reaction.users().flatten()
                players.remove(self.bot.user)
                break
        for player in players:
            try:
                await player.send("Welcome to poker, you are in a game now.")
                await self.lokkoin.remove_coins(str(player.id), 1)
            except discord.Forbidden:
                players.remove(player)
                await ctx.send(f"{player.mention} cannot play as I cannot DM them")
        if len(players) < 2:
            await ctx.send("I want a few more players please!\nTry this again when more people have reacted")
            return
        await ctx.send("Good luck everyone!")
        game = PokerGame(players, self.deck, int(
            msg.content.strip(self.start_message)))
        self.games[ctx.channel] = game
        for player in players:
            hand = ""
            for card in game.hands[player]:
                hand += f"{self.numbers[card[0]]}{self.suits[card[1]]}, "
            await player.send(f"Your hand is:\n{hand}")

    @poker.command(description="Starts off a bidding round in a game of poker")
    async def bid(self, ctx, bid: int):
        if not ctx.channel in self.games:
            await ctx.send("There isn't a game being played here")
            return
        game = self.games[ctx.channel]
        if ctx.author != game.players[game.turn % len(game.players)]:
            await ctx.send("It's not your turn")
            return
        if game.current_bid:
            await ctx.send("Please use the \"poker see\" or \"poker raise\" commands. This is only for the first bidder")
            return
        if bid < 0:
            await ctx.send("You can't have a negative bid!")
            return
        if int(await self.lokkoin.get_balance(str(ctx.author.id))) < bid:
            await ctx.send("You don't have enough coins for that")
            return
        game.bids[ctx.author] = bid
        await self.lokkoin.remove_coins(str(ctx.author.id), bid)
        game.pot += bid
        game.current_bid = [ctx.author, bid]
        game.turn += 1
        await ctx.send(f"{game.players[game.turn%len(game.players)].mention} it's your turn!")

    @poker.command(description="Raises the bid in a game of poker", name="raise")
    async def poker_raise(self, ctx, bid: int):
        if not ctx.channel in self.games:
            await ctx.send("No game of poker here")
            return
        game = self.games[ctx.channel]
        if ctx.author != game.players[game.turn % len(game.players)]:
            await ctx.send("It isn't your turn")
            return
        if not game.current_bid:
            await ctx.send("Please use the \"poker bid\" command")
            return
        if bid < 0:
            await ctx.send("No negative bids")
            return
        game.current_bid = [ctx.author, game.current_bid[1]+bid]
        game.bids[ctx.author] += bid
        if int(await self.lokkoin.get_balance(str(ctx.author.id))) < bid:
            await ctx.send("You don't have enough coins for that")
            return
        await self.lokkoin.remove_coins(str(ctx.author.id), bid)
        game.pot += bid
        game.turn += 1
        await ctx.send(f"{game.players[game.turn%len(game.players)].mention} It's your turn!")

    @poker.command(description="Sees the currnent bet in a poker game")
    async def see(self, ctx):
        if not ctx.channel in self.games:
            await ctx.send("No game of poker here")
            return
        game = self.games[ctx.channel]
        if ctx.author != game.players[game.turn % len(game.players)]:
            await ctx.send("It isn't your turn")
            return
        if not game.current_bid:
            await ctx.send("Please use the \"poker bid\" command")
            return
        if int(await self.lokkoin.get_balance(str(ctx.author.id))) < game.current_bid[1]:
            await ctx.send("You don't have enough coins for that")
            return
        await self.lokkoin.remove_coins(str(ctx.author.id), game.current_bid[1]-game.bids[ctx.author])
        game.bids[ctx.author] += game.current_bid[1]
        game.pot += game.current_bid[1]
        game.turn += 1
        if game.current_bid[0] == game.players[game.turn % len(game.players)]:
            await ctx.send("Bidding round over")
            winner = game.winner()
            await ctx.send(f"Player {winner[0].mention} wins {game.pot} lokkoins using their {winner[1]}!\nSay well done!")
            hands = ""
            for player in game.players:
                hands += player.display_name+" - "
                for card in game.hands[player]:
                    hands += f"{self.numbers[card[0]]}{self.suits[card[1]]}, "
                hands = hands[:-2]+"\n"
            await ctx.send(hands)
            await self.lokkoin.add_coins(str(ctx.author.id), game.pot)
            del self.games[ctx.channel]

    @poker.command(description="Folds in a round of poker")
    async def fold(self, ctx):
        if not ctx.channel in self.games:
            await ctx.send("No game of poker here")
            return
        game = self.games[ctx.channel]
        if ctx.author != game.players[game.turn % len(game.players)]:
            await ctx.send("It isn't your turn")
            return
        if not game.current_bid:
            await ctx.send("Please use the \"poker bid\" command")
            return
        game.turn %= len(game.players)
        game.players.remove(ctx.author)
        if len(game.players) == 1:
            winner = game.winner()
            await ctx.send(f"Player {winner[0].mention} wins {game.pot} lokkoins using their {winner[1]}!\nSay well done!")
            hands = ""
            for player in game.players:
                hands += player.display_name+" - "
                for card in game.hands[player]:
                    hands += f"{self.numbers[card[0]]}{self.suits[card[1]]}, "
                hands = hands[:-2]+"\n"
            await ctx.send(hands)

            await self.lokkoin.add_coins(str(ctx.author.id), game.pot)
            del self.games[ctx.channel]

    @poker.command(description="Shows the current bidding stats of the game")
    async def cb(self, ctx):
        if not ctx.channel in self.games:
            await ctx.send("No game of poker here")
            return
        game = self.games[ctx.channel]
        if not game.id:
            await ctx.send(f"You have bid {game.bids[ctx.author]} coins already\nTo stay in the game, you need to bid {game.current_bid[1]}\nThe total prize money for this game is {game.pot}")
            return
        await ctx.send("The game hasn't had it's first bid yet")

class PokerGame:
    def __init__(self, players, deck, stud_size):
        self.id = None
        self.players = players
        self.deck = deck
        self.turn = 0
        self.hands = {player: [] for player in players}
        for player in self.hands:
            for i in range(stud_size):
                card = random.choice(self.deck)
                self.deck.remove(card)
                self.hands[player].append(card)
            self.hands[player].sort()
        self.rankings = {"straight flush": self.straight_flush, "four of a kind": self.four_of_a_kind, "full house": self.full_house,"flush": self.flush, "straight": self.straight, "three of a kind": self.three_of_a_kind, "two pair": self.two_pair, "one pair": self.one_pair}
        self.current_bid = 0
        self.pot = len(self.players)
        self.bids = {player: 0 for player in self.players}

    def winner(self):
        rankings = [ranking for ranking in self.rankings]
        winner = [len(rankings)+1, self.players[0], [0, 0]]
        for player in self.hands:
            for ranking in rankings:
                if self.rankings[ranking](self.hands[player]):
                    value = rankings.index(ranking)
                    if value < winner[0]:
                        winner = [rankings.index(ranking), player, self.rankings[ranking](
                            self.hands[player])[1]]
                    elif value == winner[0]:
                        if self.rankings[ranking](self.hands[player])[1] > winner[2]:
                            winner = [rankings.index(ranking), player, self.rankings[ranking](
                                self.hands[player])[1]]
        return(winner[1], rankings[winner[0]])

    def straight_flush(self, hand):
        suits = [[] for i in range(4)]
        for card in hand:
            suits[card[1]].append(card[0])
        suits.reverse()
        for suit in suits:
            values = suit[:]
            for value in values:
                while values.count(value) >= 2:
                    values.remove(value)
            if len(values) >= 5:
                for i in range(len(values)-1, 3, -1):
                    if i == 4:
                        if values[i::-1] == [j for j in range(values[i],values[i]-5,-1)]:
                           return(True, hand[-1-[card[0] for card in hand[::-1]].index(values[i])])
                    if values[i:i-5:-1] == [j for j in range(values[i], values[i]-5, -1)]:
                        return(True, [i, -1-suits.index(suit)])
        return(False)

    def four_of_a_kind(self, hand):
        values = [card[0] for card in hand]
        for value in values:
            if values.count(value) >= 4:
                return(True, [value, 3])

    def full_house(self, hand):
        values = [card[0] for card in hand]
        has_three = False
        for value in values:
            if values.count(value) >= 3:
                while value in values:
                    values.remove(value)
                    value_1 = value
                has_three = True
                break
        if not has_three:
            return(False)
        for value in values:
            if values.count(value) >= 2:
                if value_1 < value:
                    value_1 = value
                return(True, value_1)
        return(False)

    def flush(self, hand):
        suits = [card[1] for card in hand]
        for suit in suits:
            if suits.count(suit) >= 5:
                return(True, hand[-1-suits.index(suit)])
        return(False)

    def straight(self, hand):
        values = [card[0] for card in hand]
        for value in values:
            while values.count(value) >= 2:
                values.remove(value)
        if len(values) < 5:
            return(False)
        for i in range(len(values)-1, 3, -1):
            if i == 4:
               if values[i::-1] == [j for j in range(values[i],values[i]-5,-1)]:
                   return(True, hand[-1-[card[0] for card in hand[::-1]].index(values[i])])
            if values[i:i-5:-1] == [j for j in range(values[i], values[i]-5, -1)]:
                return(True, hand[-1-[card[0] for card in hand[::-1]].index(values[i])])
        return(False)

    def three_of_a_kind(self, hand):
        values = [card[0] for card in hand]
        values.reverse()
        for value in values:
            if values.count(value) >= 3:
                return(True, hand[-1-values.index(value)])
        return(False)

    def two_pair(self, hand):
        values = [card[0] for card in hand]
        found = False
        for value in values:
            if values.count(value) >= 2:
                while value in values:
                    values.remove(value)
                    value1 = value
                found = True
                break
        if not found:
            return(False)
        for value in values:
            if value < value1:
                value = value1
            if values.count(value) >= 2:
                return(True, hand[-1-values.index(value)])
        return(False)

    def one_pair(self, hand):
        values = [card[0] for card in hand]
        for value in values:
            if values.count(value) >= 2:
                return(True, hand[-1-values.index(value)])
        return(False)


def setup(bot):
    bot.add_cog(Games(bot))
