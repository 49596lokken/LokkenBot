import discord
from discord.ext import commands
import random


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.dos_class = Dos()
        self.xo_channels = {}
        self.c4_channels = {}


    def get_channel(self, ctx):
        if ctx.guild:
            return(f"{ctx.guild.id} {ctx.channel.id}")
        return(None)


    @commands.Cog.listener()
    async def on_ready(self):
        self.dos_class.cards = {}
        for emoji in self.bot.get_guild(721340744207695903).emojis:
            if emoji.name.lower() == "cardback":
                self.dos_class.cardback = str(emoji)
            else:
                self.dos_class.cards[emoji.name.lower().replace("_", "#")] = str(emoji)

    @commands.group(pass_context=True,invoke_without_command=True)
    async def dos(self, ctx):
        ...
    @dos.command(name="enable")
    async def dos_enable(self, ctx):
        await ctx.send(self.dos_class.enable(self.get_channel(ctx)))

    @dos.command(name="disable")
    async def dos_disable(self,ctx):
        await ctx.send(self.dos_class.disable(self.get_channel(ctx)))


    @dos.command(description="Prepares a channel for a game of dos",name="ready")
    async def dos_ready(self, ctx):
        ready = self.dos_class.ready(self.get_channel(ctx))
        if ready == "Game ready":
            startmsg = await ctx.send(f"Please react to this message to be added to the dos game. One everyone has reacted, {ctx.author.mention} should execute the \"dos start\" command to start the game")
            await startmsg.add_reaction("\U0000270B")
            game = self.dos_class.games[self.get_channel(ctx)]
            game.start_id = startmsg.id
            game.start_author=ctx.author
            return
        await ctx.send(ready)

    @dos.command(description="Starts a game of dos in the channel",name="start")
    async def dos_start(self, ctx):
        game = self.dos_class.get_game(self.get_channel(ctx))
        if game:
            if game.started:
                await ctx.send("Game already started")
                return
            startmsg = await ctx.fetch_message(game.start_id)
            for reaction in startmsg.reactions:
                if reaction.emoji=="\U0000270B":
                    players = await reaction.users().flatten()
                    players.remove(self.bot.user)
                    break
            for player in players:
                try:
                    await player.send("Welcome to dos, you are in a game now.")
                    dos_player = DosPlayer(game)
                    game.players[player] = dos_player
                except discord.Forbidden:
                    players.remove(player)
                    await ctx.send(f"{player.mention} cannot play as I cannot DM them")
            if len(players) < 2:
                msg = discord.Embed(title = "Click here to see the message", url=f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{game.start_id}")
                await ctx.send(f"Sorry, not enough players reacted so the game cannot be started",embed=msg)
                return
            game.started=True
            spain, uk = "\U0001f1ea\U0001f1f8", "\U0001f1ec\U0001f1e7"
            choose_rules = await ctx.send(f"Please choose rules: {spain} or {uk}")
            await choose_rules.add_reaction(spain)
            await choose_rules.add_reaction(uk)
            def check(reaction, user):
                return(str(reaction.emoji) in [spain, uk] and user==ctx.author)
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            game.rules = "uk"
            if str(reaction.emoji) == spain:
                game.rules = "spain"
            rules = open(f"assets/games/dos/howto-{game.rules}.txt")
            await ctx.send(rules.read())
            rules.close()
            await ctx.send("Try the \"help dos\" for help")
            random.shuffle(players)
            for i in range(7):
                for player in players:
                    dos_player=game.players[player]
                    dos_player.draw_card()
            for player in players:
                await player.send(game.players[player].get_hand())
            for i in range(2):
                card = random.choice(game.deck)
                game.centre_row.append(card)
                game.deck.remove(card)
            await ctx.send(f"{game.current_player().mention}, it is your turn")
            await ctx.send(game.get_centre_row())
            
        else:
            await ctx.send("Try \"dos ready\"")


    @dos.command(description="plays cards onto pile. Last card specified is the pile to be played onto\ncards are formatted as (first letter of colour)(number) or just dos if it is a 2",name="play")
    async def dos_play(self, ctx, *cards):
        game = self.dos_class.get_game(self.get_channel(ctx))
        if not game:
            await ctx.send("please use \"dos ready\"")
            return
        if not game.started:
            await ctx.send("please use \"dos start\"")
            return
        if ctx.author != game.current_player():
            await ctx.send("It isn't your turn")
            return
        if game.played and game.rules=="spain":
            await ctx.send("You have aready played. To add a newpile use the \"dos newpile \" command")
            return
        if len(game.centre_row) == 0:
            await ctx.send("No cards to play on")
            return
        if not game.can_play:
            await ctx.send("You already added a new pile!")
            return
        cards = [card.lower() for card in cards]
        matched = game.is_match(cards)
        if not matched[0]:
            await ctx.send("The cards did not form a match")
            return
        game.played = True
        if game.rules == "spain":
            game.centre_row.append(cards[len(cards)-2])
        for i in range(len(cards)):
            if i == len(cards)-1:
                game.centre_row.remove(cards[i])
            else:
                game.players[ctx.author].hand.remove(cards[i])
        await ctx.author.send(game.players[ctx.author].get_hand())
        await ctx.send(game.get_centre_row())
        if matched[1]:
            await ctx.send("Colour match")
            game.colour_matches += 1
            if len(cards) == 3:
                for player in game.players:
                    if player != ctx.author:
                        game.players[player].draw_card()
                    await player.send(game.get_player(player).get_hand())
    
    @dos.command(description="Adds a new pile",name="newpile")
    async def dos_newpile(self, ctx, newpile):
        game = self.dos_class.get_game(self.get_channel(ctx))
        if not game:
            await ctx.send("There is no game here")
            return
        if not game.started:
            await ctx.send("Game not started")
            return
        if ctx.author != game.current_player():
            await ctx.send("It isn't your turn")
            return
        if game.rules == "uk" and game.can_play:
            game.can_play = False
            while len(game.centre_row) < 2:
                card = random.choice(game.deck)
                game.centre_row.append(card)
                game.deck.remove(card)
        if game.colour_matches == 0:
            await ctx.send("You have no piles to add. type \"dos next\" to go onto the next turn")
            return
        dos_player = game.get_player(ctx.author)
        if not newpile in dos_player.hand:
            await ctx.send("You don't have that card")
            return
        await ctx.send("New pile added")
        game.can_play = False
        game.colour_matches -= 1
        dos_player.hand.remove(newpile)
        game.centre_row.append(newpile)
        await ctx.author.send(dos_player.get_hand())
        await ctx.send(game.get_centre_row())


    @dos.command(description="Ends your turn", name="next")
    async def dos_next(self,ctx):
        game = self.dos_class.get_game(self.get_channel(ctx))
        if not game:
            await ctx.send("There is no game here")
            return
        if not game.started:
            await ctx.send("Game not started")
            return
        if ctx.author != game.current_player():
            await ctx.send("It isn't your turn")
            return
        dos_player = game.get_player(ctx.author)
        if len(dos_player.hand) == 0:
            await ctx.send(f"{ctx.author.mention} has won the game. Congratulations!")
            self.dos_class.games[self.get_channel(ctx)] = None
            lokkoins = self.bot.get_cog("lokkoin")
            if lokkoins:
                balance = await lokkoins.get_balance(str(ctx.author.id))
                if balance:
                    await lokkoins.add_coins(str(ctx.author.id), 100)
                    await ctx.send(f"{ctx.author.display_name} got 100 lokkoins for winning!")
            return
        if game.colour_matches != 0:
            await ctx.send(f"You cannot go onto the next turn as you have {game.colour_matches} new piles to add")
            return
        if not game.played:
            await game.current_player().send("You didn't play. Picking up a card")
            dos_player.draw_card()
        game.turn += 1
        game.played = False
        game.can_play = True
        while len(game.centre_row) < 2:
            card = random.choice(game.deck)
            game.deck.remove(card)
            game.centre_row.append(card)
        await ctx.send(f"{game.current_player().mention} It's your turn!")
        await ctx.send(game.get_centre_row())
        await game.current_player().send(game.get_player(game.current_player()).get_hand())

    @dos.command(description="Shows the centre row",aliases=["piles"],name="centre")
    async def dos_centre(self,ctx):
        game = self.dos_class.get_game(self.get_channel(ctx))
        if not game:
            await ctx.send("There is no game here")
            return
        if not game.started:
            await ctx.send("Game not started")
            return
        await ctx.send(game.get_centre_row())
    
    @dos.command(description="shows you your hand",name="hand")
    async def dos_hand(self,ctx):
        game = self.dos_class.get_game(self.get_channel(ctx))
        if not game:
            await ctx.send("There is no game here")
            return
        if not game.started:
            await ctx.send("Game not started")
            return
        await ctx.author.send(game.get_player(ctx.author).get_hand())


class Dos:
    def __init__(self):
        self.games = {}
        self.cards = {}
        channels=open("data/games/dos/channels", "r")
        for channel in channels:
            self.games[channel[:-1]] = None
        channels.close()

    def get_game(self, channel):
        if not channel in self.games:
            return(None)
        return(self.games[channel])
        

    def enable(self, channel):
        if not channel:
            return("Please do this in a guild")
        if channel in self.games:
            return("Already a dos channel")
        else:
            self.games[channel] = None
            channels=open("data/games/dos/channels", "a")
            channels.write(channel+"\n")
            return("The channel is now a dos channel")

    def ready(self, channel):
        if not channel in self.games:
            return("Dos has not been enabled in this channel")
        if self.games[channel]:
            return("There is already a waiting game")
        self.games[channel] = DosGame(self)
        return("Game ready")

    def disable(self, channel):
        if channel in self.games:
            del self.games[channel]
            return("No longer a dos channel")
        else:
            return("This isn't a dos channel")


    def is_card(self, card):
        return card in self.cards

    def get_card(self, card):
        return self.cards[card]


class DosGame:
    def __init__(self, dos):
        self.dos = dos
        self.deck = []
        duplicates = 3
        for card in dos.cards:
            if card[1] == "6":
                duplicates = 2
            elif card == "dos":
                duplicates = 12
            for i in range(duplicates):
                self.deck.append(card)
        self.players = {}
        self.started = False
        self.turn = 0
        self.start_id = 0
        self.start_author = None
        self.discards = []
        self.centre_row = []
        self.colour_matches = 0
        self.rules = ""
        self.played = False
        self.can_play = True
    
    def current_player(self):
        return(list(iter(self.players))[self.turn % len(self.players)])

    def get_player(self, player):
        if player in self.players:
            return(self.players[player])
        return None

    def card_in_deck(self, card):
        return (card in self.deck)
    
    def reshuffle(self):
        random.shuffle(self.discards)
        self.deck=self.discards[:]
        self.discards = []

    def get_centre_row(self):
        if len(self.centre_row) == 0:
            return("The centre row is empty")
        output = ""
        for card in self.centre_row:
            output += self.dos.get_card(card)
        return(output)
    
    def is_match(self, played_cards):
        cards = played_cards[:]
        if len(cards) == 2:
            return([cards[0][1]==cards[1][1] or "#" in cards[0][1]+cards[1][1], cards[0][0] == cards[1][0] or "dos" in cards])
        else:
            #makes dos cards into 2s
            while "dos" in cards:
                if cards.index("dos") != 2:
                    if cards[2] == "dos":
                        return([False, False])
                    cards[cards.index("dos")] = cards[2][0]+"2"
                else:
                    cards[2] = cards[0][0]+"2"
            #deals with wild # cards
            possible_sums=[]
            if cards[0][1].isdigit():
                if cards[1][1].isdigit():
                    possible_sums = [int(cards[0][1:])+int(cards[1][1:])]
                else:
                    possible_sums = [i+1 for i in range(int(cards[0][1:]), 10)]
            else:
                if cards[1][1].isdigit():
                    possible_sums = [i+1 for i in range(int(cards[1][1:]), 10)]
                else:
                    possible_sums = [i+1 for i in range(1, 10)]
            output = []
            if cards[2][1].isdigit():
                if int(cards[2][1:]) in possible_sums:
                    output.append(True)
            elif len(possible_sums) != 0:
                output.append(True)
            else:
                return([False, False])
            output.append(cards[0][0]==cards[1][0] and cards[0][0] == cards[2][0])
            return(output)
            
        
class DosPlayer:
    def __init__(self, game):
        self.game = game
        self.hand=[]
        
    
    def draw_card(self):
        if len(self.game.deck) == 0:
            self.game.reshuffle()
        card = random.choice(self.game.deck)
        self.game.deck.remove(card)
        self.hand.append(card)

    def get_hand(self):
        if len(self.hand) == 0:
            return("You have no cards")
        output = ""
        for card in self.hand:
            output += self.game.dos.get_card(card)
        return(output)


def setup(bot):
    bot.add_cog(Games(bot))