import discord
from discord.ext import commands
from assets.games.dos.classes import *
from assets.games.xo.classes import *
from assets.games.c4.classes import *
import random
import asyncio


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.dos_class = Dos()
        for emoji in self.bot.get_guild(721340744207695903).emojis:
            if emoji.name.lower() == "cardback":
                self.dos_class.cardback = str(emoji)
            else:
                self.dos_class.cards[emoji.name.lower().replace("_", "#")] = str(emoji)
        self.xo_channels = {}
        self.c4_channels = {}


    def get_channel(self, ctx):
        if ctx.guild:
            return(f"{ctx.guild.id} {ctx.channel.id}")
        return(None)

#DOS - made originally by Matel
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


#Nougths and crosses
    @commands.group(pass_context=True,invoke_without_command=True)
    async def xo(self, ctx):
        ...

    @xo.command(description="Starts a noughts and crosses with a specified person", brief="author of message starts", name="start")
    async def xo_start(self, ctx, opponent: commands.MemberConverter, wager=0):
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

#Connect 4
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

                
            
     
    

def setup(bot):
    bot.add_cog(Games(bot))