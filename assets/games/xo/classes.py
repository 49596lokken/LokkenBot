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