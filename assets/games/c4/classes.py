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
    
    
