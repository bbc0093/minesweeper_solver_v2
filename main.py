import numpy as np

import gym
from gym import spaces

from parse_game import game

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

class minesweep(gym.Env):
    """this is an interface to Microsoft's minesweeper game
    
    After each step the agent receives an observation of:
    0 - Game is still going
    1 - Game is lost
    2 - Game is won
    
    The rewards is calculated as:
    1 - for a won game
    -1 - for a lost game
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        self.game = game("9x9")
        self.game.find_game()
        self.game.update_board()
        self.actions = 0
        
        self.reward_range = (-1, (self.game.board_w-1)*(self.game.board_h-1))
        
        self.action_space = spaces.MultiDiscrete([self.game.board_w, self.game.board_h, 2])   #X, Y, R/L
        
        self.observation_space = spaces.MultiDiscrete([self.game.board_w, self.game.board_h, 10])   #X, Y, val
    
    def _take_action(self, action):
                
        x  = action[0]
        y  = action[1]
        rl = action[2]

        if(not self.game.is_valid_loc(x, y)):
            return 1

        if(rl):
            self.game.click(x, y)
        else:
            self.game.right_click(x, y)
    
    def gen_obs(self):
        x = np.array()
        y = np.array()
        val = np.array()
        for row in range(self.board_h):
            for col in range(self.board_w):
                x.append(col)
                y.append(row)
                val.append(self.board[col + row * self.board_w] + 1)
    
        return np.array(x, y, val)
    
    def step(self, action):
        assert self.action_space.contains(action)
        repeat = self._take_action(action)
        
        if(repeat):
            return self.obs, 0, 0, {}
        
        if(not self.game.result):
            done = 0
            self.actions += 1
            reward = self.actions
        elif(self.game.result == "won"):
            done = 1
            reward = (self.game.board_w-1)*(self.game.board_h-1)
        elif(self.game.result == "lost"):
            done = 1
            reward = -1
            
        self.obs = self.gen_obs()
        
        return self.obs, reward, done, {}
    
    def render(self):
        self.game.print_board()
    
    def reset(self):
        self.actions = 0
        self.game.reset()
    

if (__name__ == "__main__"):
    env = minesweep()
    
    """EXAMPLE:
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    nb_actions = env.action_space.n
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print(model.summary())
    policy = EpsGreedyQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
    target_model_update=1e-2, policy=policy)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])
    
    # Okay, now it's time to learn something! We visualize the training here for show, but this slows down training quite a lot. 
    dqn.fit(env, nb_steps=5000, visualize=True, verbose=2)
    """
    
    