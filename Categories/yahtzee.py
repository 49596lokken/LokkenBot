import discord
from discord.ext import commands
import random


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.games = {}

    def get_channel(self, ctx):
        return(f"{ctx.guild.id} {ctx.channel.id}")

    @commands.group(pass_context=True,invoke_without_command=True,description="Yahtzee games in discord.\nYou may not recognise some categories or think that some of the scoring is wrong and that is because this is Norwegian Yahtzee which is apparently different")
    async def yahtzee(self, ctx):
        ...
    
    @yahtzee.command(description="starts a game of Yahtzee in the channel with the specified people")
    async def start(self, ctx, *players: commands.MemberConverter):
        channel = self.get_channel(ctx)
        if channel in self.games:
            await ctx.send(f"A game is already happening in here. The players are {[player.display_name for player in self.games[channel].players]}")
        players = [player for player in players]
        if not ctx.author in players:
            players.append(ctx.author)
        self.games[channel] = YahtzeeGame(players)
        await ctx.send(f"Game started with {[player.name for player in players]}")
    
    @yahtzee.command(description="Shows the scorecards for a player")
    async def scores(self, ctx, player: commands.MemberConverter):
        channel = self.get_channel(ctx)
        if not channel in self.games:
            await ctx.send("No game happening here")
            return
        game = self.games[channel]
        for person in game.scores:
            if player == person:
                score = game.scores[player]
                description=""
                for category in score:
                    description += category
                    if score[category] == None:
                        description += " - []\n"
                    else:
                        description += f" - {score[category]}\n"
                description += "\nbonus - "
                if game.has_bonus(player):
                    description += "50"
                else:
                    description += "[]"
                e = discord.Embed(title=f"Scorecard of {person.display_name}", description=description)

                await ctx.send(embed=e)
                return
        await ctx.send("That person isn't playing")
    
    @yahtzee.command(description="Performs a Yahtzee roll")
    async def roll(self, ctx):
        channel = self.get_channel(ctx)
        if not channel in self.games:
            await ctx.send("No game happening here")
            return
        game = self.games[channel]
        if game.players[game.turns_taken%len(game.players)] != ctx.author:
            await ctx.send("It's not your turn")
            return
        if game.rolls == 3:
            await ctx.send("You have already rolled too many times")
            return
        if game.diceroll:
            game.diceroll = [game.diceroll[i] for i in game.keeping]
            game.keeping = [i for i in range(len(game.diceroll))]
            for i in range(5-len(game.diceroll)):
                game.diceroll.append(random.randint(1,6))
        else:
            game.diceroll = [random.randint(1,6) for i in range(5)]
        output = ""
        for die in game.diceroll:
            output += f"{die} "
        game.rolls += 1
        await ctx.send(f"You rolled\n{output}")
    
    @yahtzee.command(description="Specifies which dice you wish to keep. To keep a type it's number from the left. E.g. if you roll 6 1 3 5 4 and want to keep the 6 and 5, type keep 1 4")
    async def keep(self, ctx, *keeping: int):
        channel = self.get_channel(ctx)
        if not channel in self.games:
            await ctx.send("No game happening here")
            return
        game = self.games[channel]
        if game.players[game.turns_taken%len(game.players)] != ctx.author:
            await ctx.send("It's not your turn")
            return
        if not game.diceroll:
            await ctx.send("You haven't rolled")
            return
        keeping = [i for i in keeping]
        game.keeping = []
        for die in keeping:
            if die-1 in game.keeping:
                await ctx.send(f"You tried to keep die number {die} twice!")
            elif die > 5:
                await ctx.send("You don't have that many dice!")
            elif die < 1:
                await ctx.send("Die numbers start at one!")
            else:
                game.keeping.append(die-1)
        await ctx.send(f"To confirm, you chose to keep {[game.diceroll[i] for i in game.keeping]} out of {game.diceroll}\n You can now either roll again or use the yahtzee play command")

    @yahtzee.command(description="Plays a set of dice to your yahtzee game")
    async def play(self, ctx, *category):
        channel = self.get_channel(ctx)
        if not channel in self.games:
            await ctx.send("No game happening here")
            return
        game = self.games[channel]
        if game.players[game.turns_taken%len(game.players)] != ctx.author:
            await ctx.send("It's not your turn")
            return
        if not game.diceroll:
            await ctx.send("You haven't rolled")
            return
        temp = category[:]
        category = ""
        for i in temp:
            category += f"{i} "
        del temp
        category = category[:-1]
        if not category in game.categories:
            await ctx.send(f"{category} is an invalid category name")
            return
        if game.scores[ctx.author][category] != None:
            await ctx.send(f"You've already played on that category. You got {game.scores[ctx.author][category]} points on it")
            return
        game.scores[ctx.author][category] = game.categories[category](game.diceroll)
        await ctx.send(f"Successfully played {game.categories[category](game.diceroll)} on the {category}")
        game.diceroll = []
        game.turns_taken += 1
        game.keeping = []
        game.rolls = 0
        scorecard = ""
        if game.turns_taken == len(game.players)*15:
            await ctx.send("The game is over!")
            winner = [None, -1]
            for player in game.scores:
                total = 0
                for category in game.scores[player]:
                    total += game.scores[player][category]
                if game.has_bonus(player):
                    total += 50
                scorecard += f"{player.display_name} - {game.scores[player][category]}\n"
                if total > winner[1]:
                    winner = [player, total]
            await ctx.send(f"Congratulations to {winner[0].mention} who won the game!\nThe scores were\n{scorecard}\n")
            del self.games[channel]
            return
        await ctx.send(f"{game.players[game.turns_taken%len(game.players)].mention} its your turn")
        




class YahtzeeGame:
    def __init__(self, players):
        self.players = players
        self.categories = {"ones":self.get_number_function(1), "twos":self.get_number_function(2), "threes":self.get_number_function(3), "fours":self.get_number_function(4), "fives":self.get_number_function(5), "sixes":self.get_number_function(6), "1 pair":self.pair, "2 pair":self.two_pair, "3 alike":self.three_alike, "4 alike":self.four_alike, "little straight":self.small_straight, "big straight":self.big_straight, "house":self.house, "chance":sum, "yahtzee":self.yahtzee}
        self.scores = {player:{category:None for category in self.categories} for player in self.players}
        self.turns_taken = 0
        self.diceroll = []
        self.keeping = []
        self.rolls = 0

    def has_bonus(self, player):
        score = 0
        for i in ["ones", "twos", "threes", "fours", "fives", "sixes"]:
            if self.scores[player][i]:
                score += self.scores[player][i]
        return(score>=63)

    def get_number_function(self, number):
        def function(diceroll):
            output = 0
            for die in diceroll:
                if die == number:
                    output += number
            return(output)
        return(function)
    
    def pair(self, diceroll):
        for number in range(6, 0, -1):
            occurences = 0
            for die in diceroll:
                if die == number:
                    occurences += 1
            if occurences >= 2:
                return(2*number)
        return(0)
    
    def two_pair(self, diceroll):
        pairs = []
        for number in range(6, 0, -1):
            occurences = 0
            for die in diceroll:
                if die == number:
                    occurences += 1
            if occurences >= 2:
                pairs.append(number)
        if len(pairs) >= 2:
            return(2*pairs[0] + 2*pairs[1])
        return(0)
    
    def three_alike(self, diceroll):
        for number in range(6, 0, -1):
            occurences = 0
            for die in diceroll:
                if die == number:
                    occurences += 1
            if occurences >= 3:
                return(3*number)
        return(0)
    
    def four_alike(self, diceroll):
        for number in range(6, 0, -1):
            occurences = 0
            for die in diceroll:
                if die == number:
                    occurences += 1
            if occurences >= 4:
                return(4*number)
        return(0)
    
    def small_straight(self, diceroll):
        diceroll.sort()
        if diceroll == [1,2,3,4,5]:
            return(15)
        return(0)
    
    def big_straight(self, diceroll):
        diceroll.sort()
        if diceroll == [2,3,4,5,6]:
            return(20)
        return(0)

    def house(self, diceroll):
        house_parts = [None, None]
        for number in range(6, 0, -1):
            occurences = 0
            for die in diceroll:
                if die == number:
                    occurences += 1
            if occurences >= 3:
                house_parts[0] = number
            elif occurences >=2:
                house_parts[1] = number
        if None in house_parts:
            return(0)
        return(house_parts[0]*3+house_parts[1]*2)

    def yahtzee(self, diceroll):
        first_number = diceroll[0]
        for die in diceroll:
            if die != first_number:
                return(0)
        return(50)

def setup(bot):
    bot.add_cog(Games(bot))