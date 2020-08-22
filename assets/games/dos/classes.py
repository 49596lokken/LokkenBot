import random

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
        random.shuffle(discards)
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


