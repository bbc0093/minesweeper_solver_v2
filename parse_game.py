from image_search import *
import cv2
import pyautogui as gui
import numpy as np
import imutils
import sys

tiles_loc = "MSsweeper/"
tiles = ["un.png", "1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "8.png", "flag.png"]


class game():
    scale = 1.2575575575575577  # the game may be resized or on a different resolution than the reference image was captured at.
                    # On init, account for that then scale all of the images appropriately
    
    def __init__(self, difficulty):
        self.difficulty = difficulty
        
        if(difficulty == "9x9"):
            self.board_w = 9
            self.board_h = 9
            
        elif(difficulty == "16x16"):
            self.board_w = 16
            self.board_h = 16
        
        self.result = None
        self.create_board()
    
    def create_board(self):
        """ 
            Create a board object. This is a 1d array representing all the elements on the board
            -1   - is an unknown space (init of all spaces)
            9    - is a known bomb
            0-8  - number space
        """
        self.board = [ 0 for _ in range(self.board_w * self.board_h)]
    
    def screen_to_board(self, x, y):
        """ 
            Convert form screen (x, y) cords to board position
        """
        bX = (x - self.x)*(self.board_w/self.w)
        bY = (y - self.y)*(self.board_h/self.h)
        return(int(bX+.2), int(bY+.2))
    
    def board_to_screen(self, bX, bY):
        """ 
            Convert form board (x, y) cords to screen position
        """
        x = (bX+.5) * (self.w/self.board_w) + self.x
        y = (bY+.5) * (self.h/self.board_h) + self.y
        
        return(x, y)
    
    def check_victory(self):
        im = gui.screenshot()
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        
        x, y = imagesearch(tiles_loc + "reset.png", img_gray, self.scale, precision=.7)
        if x != -1 and y != 1: 
            self.result = None
            return self.result
    
        x, y = imagesearch(tiles_loc + "reset_lost.png", img_gray, self.scale, precision=.7)
        if x != -1 and y != 1: 
            self.result = "lost"
            return self.result
            
        x, y = imagesearch(tiles_loc + "reset_won.png", img_gray, self.scale, precision=.7)
        if x != -1 and y != 1: 
            self.result = "won"
            return self.result
    
    def update_board(self):
        im = gui.screenshot()
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        
        self.create_board()  #opencv struggles to detect the '0' tiles, so detect everything else
        
        for num, tile in enumerate(tiles):
            if(num == 0): # opencv can't detect the 0 so detect the unknown
                num = -1

            matches = imagesearch_all(tiles_loc + tile, img_gray, self.scale, .85)
            
            if not matches:
                continue
            
            for (x, y) in zip(matches[1], matches[0]):
                bX, bY = self.screen_to_board(x, y)
                if(self.out_of_board(bX, bY)):
                    continue
                self.board[bX + self.board_w * bY] = num
    
        self.check_victory()
        
        
    def num_known(self):
        num = 0
        for item in self.board:
            if item != -1 and item != 9:
                num += 1
        
        return num
    
    def print_board(self):
        for row in range(self.board_h):
            ary = [str(self.board[i + row * self.board_w]) for i in range(self.board_w)]
            print(ary)
    
    def out_of_board(self, x, y):
        if(x < 0 or x >= self.board_w):
            return 1
        
        if(y < 0 or y >= self.board_h):
            return 1
        
        return 0
    
    def find_game_scale(self):
        if(self.difficulty == "9x9"):
            image = tiles_loc + "beginner.png"
        elif(self.difficulty == "16x16"):
            image = tiles_loc + "intermediate.png"
        else:
            print("find_game_scale: board image not defined")
            return -1
        
        print("Finding game scale and position..")
        
        print("DEV SEARCH:")
        scale = find_scale(image, .85, 2, start_val = self.scale)
        
        if(scale):
            return scale
        print("Basic Search:")
        
        scale = find_scale(image, .9, 10)
        
        if(scale):
            return scale
        
        print("Intermediate Search:")
        scale = find_scale(image, .85, 300)
        
        if(scale):
            return scale
        
        print("Advanced Search:")
        scale = find_scale(image, .85, 1000)
        
        return scale

    def find_game(self):
        self.scale, self.x, self.y, self.w, self.h = self.find_game_scale()
        print(self.scale, self.x, self.y, self.w, self.h)
    
    def click(self, bX, bY):
        x, y = self.board_to_screen(bX, bY)
        gui.click(x=x, y=y)
        
    def right_click(self, bX, bY):
        x, y = self.board_to_screen(bX, bY)
        gui.click(x=x, y=y, button='right')
        
    def get_board_size(self):
        return self.board_h * self.board_w
        
    def run(self):
        input("continue...")
        self.click(0,0)
        #self.click(15,15)
        self.update_board()
        self.print_board()
        self.reset()
    
    def is_valid_loc(self, x, y):
        return self.board[x + y * self.board_w] == -1
    
    def reset(self):
        print("Reset")
        im = gui.screenshot()
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        
        x, y = imagesearch(tiles_loc + "reset.png", img_gray, self.scale, precision=.7)
        if x != -1 and y != 1: 
            gui.click(x+1, y+1)
    
        x, y = imagesearch(tiles_loc + "reset_lost.png", img_gray, self.scale, precision=.7)
        if x != -1 and y != 1: 
            gui.click(x+1, y+1)
            
        x, y = imagesearch(tiles_loc + "reset_won.png", img_gray, self.scale, precision=.7)
        if x != -1 and y != 1: 
            gui.click(x+1, y+1)
            
        self.result = None
    
if __name__ == "__main__":
    g = game("9x9")
    g.find_game()
    g.run()
    
    