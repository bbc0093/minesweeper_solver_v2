""" Python implementation of minesweeper to reduce
    run time and prevent need for mouse takeover"""

import random

#difficulties
BEGINNER = 0
INTERMEDIATE = 1
ADVANCED = 2

#move responces
MOVE_INV = -1
MOVE_DUP = 0
MOVE_LOST = 1
MOVE_WON = 2
MOVE_CONTINUE = 3

MS_DEBUG = False

class minesweeper():
    def __init__(self):
        self.is_first = True
        self.recursive = 0
        self.chooseDifficultyLevel(BEGINNER)
        self.initialise()
        self.print_int_board()
        self.place_mines()
        self.print_int_board()
        self.pop_board()
        self.print_int_board()
        
        
    def chooseDifficultyLevel(self, level):
        if level == BEGINNER:
            self.side = 9;
            self.mines = 10;
    
        if level == INTERMEDIATE:
            self.side = 16;
            self.mines = 40;
    
        if level == ADVANCED:
            self.side = 24;
            self.mines = 99;

    def is_valid(self, row, col):
        return (row >= 0) and (row < self.side) and \
        (col >= 0) and (col < self.side);
        
    def is_mine(self, row, col):
        return self.int_board[row][col] == "*"
    
    def is_known(self, row, col):
        return not self.known_board[row][col] == "-"
    
    def print_board(self):
        r = [" ", "|"]
        for col in range(self.side):
            r.append(str(col))
        print(r)
        r = ["_"] * (self.side +2)
        print(r)
        for row in range(self.side):
            r = [str(row), "|"]
            for col in range(self.side):
                r.append(str(self.known_board[row][col]))
            print(r)
        print()
        print()
        
    def print_int_board(self):
        if not MS_DEBUG:
            return 
        
        for row in range(self.side):
            r = []
            for col in range(self.side):
                r.append(str(self.int_board[row][col]))
            print(r)
        print()
        print()

    def countAdjacentMines(self, row, col):
        count = 0
        
        for row_off in range(-1, 2):
            for col_off in range(-1, 2):
                tmp_row = row_off + row
                tmp_col = col_off + col
                if not self.is_valid(tmp_row, tmp_col):
                    continue
                
                if self.is_mine(tmp_row, tmp_col):
                    count += 1
            
        return count

    def replace_mine(self, old_row, old_col):
        """ A function to replace the mine from (row, col) and put it to a vacant space
            This is done so first click is not a mine
        """
        for row in range(self.side):
            for col in range(self.side):
                if self.int_board[row][col] != '*':
                    self.int_board[row][col] = "*"
                    self.int_board[old_row][old_col] = "-"
                    return

       
    def initialise(self):
        self.int_board = []
        self.known_board = []
        
        for row in range(self.side):
            tmp_row = []
            tmp_known_row = []   #python stores in lists by reference so either do this or use the copy function
            for col in range(self.side):
                tmp_row.append(0)
                tmp_known_row.append('-')
            
            self.int_board.append(tmp_row)
            self.known_board.append(tmp_known_row)
        
    def place_mines(self):
        random.seed()
        
        store = []
        
        while len(store) < self.mines:
            rand = random.randrange(self.side*self.side)
            
            if rand in store :
                continue
            
            store.append(rand)
            
            row = int(rand / self.side)
            col = int(rand % self.side)
            self.int_board[row][col] = "*"
            
    def pop_board(self):
        for row in range(self.side):
            for col in range(self.side):
                if self.is_mine(row, col):
                    continue
                
                self.int_board[row][col] = self.countAdjacentMines(row, col)
                
     
    def check_won(self):
        for row in range(self.side):
            for col in range(self.side):
                if self.known_board[row][col] == "-" and not self.int_board[row][col] == "*":
                    return False
        
        return True
        
    def make_move(self, row, col):
        
        if not self.is_valid(row, col):
            print("invalid move", row, col, self.row)
            return MOVE_INV
        
        if self.is_known(row, col):
            if not self.recursive:
                print("dup move", row, col)
            return MOVE_DUP
        
        if self.is_first and self.is_mine(row, col):
            self.replace_mine(row, col)
            self.pop_board()
                
        self.is_first = False
                
        self.known_board[row][col] = self.int_board[row][col]
        
        if self.is_mine(row, col):
            print("YOU LOST!!")
            return MOVE_LOST

        if self.int_board[row][col] == 0:
            self.recursive += 1
            
            for new_row in range(-1, 2):
                for new_col in range(-1, 2):
                    if not self.is_valid(new_row+row, new_col+col):
                        continue
                    self.make_move(new_row+row, new_col+col)
                    
            self.recursive -= 1

        if self.check_won():
            print("YOU WON!!")
            return MOVE_WON
        
        return MOVE_CONTINUE

#wrapper to fit ML alg
class game(minesweeper):
    def __init__(self, size):
        print("Starting...")
        if size == "9x9":
            minesweeper.__init__(self)
            
        self.board_w = self.side
        self.board_h = self.side
        self.result = None
            
    def click(self, row, col):
        print("Click: " + str(row) + ", " + str(col))
        last_result = self.make_move(row, col)
        if last_result == MOVE_WON:
            self.result = "won"
        elif last_result == MOVE_LOST:
            self.result = "lost"
        else:
            self.result = None

    def right_click(self, row, col):
        print("Not implemented")

    def find_game(self):
        pass
    
    def update_board(self):
        self.board = []
        
        for row in range(self.side):
            for col in range(self.side):
                if self.int_board[row][col] == "-":
                    self.board.append(-1)
                if self.int_board[row][col] == "*":
                    self.board.append(9)
                else:
                    self.board.append(self.int_board[row][col])
    
    def is_valid_loc(self, row, col):
        return self.is_valid(row, col) and not self.is_known(row, col)
    
    def get_board_size(self):
        return self.board_w * self.board_h

    def reset(self):
        print("Reset")
        minesweeper.__init__(self)
        self.update_board()
    
    def num_known(self):
        num = 0
        for row in range(self.side):
            for col in range(self.side):
                if self.known_board[row][col] != "-":
                    num += 1
    
        return num
    
if __name__ == "__main__":
    game_inst = minesweeper()
    result = MOVE_CONTINUE
    while result != MOVE_WON and result != MOVE_LOST:
        row = int(input("Move (row):"))
        col = int(input("Move (col):"))
        result = game_inst.make_move(row, col)
        game_inst.print_board()
    
    print(result)