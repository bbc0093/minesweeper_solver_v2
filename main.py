import numpy as np

import gym
from gym import spaces

from parse_game import game

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.sarsa import SARSAAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

class minesweep(gym.Env):
    """this is an interface to Microsoft's minesweeper game
    
    After each step the agent receives an observation of:
    Current board state
    
    The rewards is calculated as:
    +1 for not repeats that don't lose the game 
    WxH - for a won game
    0 - for a lost game
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        self.game = game("9x9")
        self.game.find_game()
        self.game.update_board()
        self.actions = 0
        
        self.reward_range = (-1, (self.game.board_w-1)*(self.game.board_h-1), np.int64)
        
        # One action per board position * R/L: Click
        self.action_space = spaces.Discrete(self.game.board_w * self.game.board_h * 2)
        
        #-1 is unknown 0-8 are num values, 9 is known bomb
        self.observation_space = spaces.Box(-1, 9, (self.game.board_w, self.game.board_h))   #X, Y, val
    
    def _take_action(self, action):
        rl = int(action % 2)
        action /= 2     
        
        x = int(action % self.game.board_w)
        action /= self.game.board_w
        
        y = int(action)
        

        if(not self.game.is_valid_loc(x, y)):
            return 1

        if(rl):
            self.game.click(x, y)
        else:
            self.game.right_click(x, y)
            
        self.game.update_board()
    
    def obs_size(self):
        return self.game.board_w * self.game.board_h * 10
    
    def action_size(self):
        return self.game.board_w * self.game.board_h * 2
    
    def gen_obs(self):
        x = np.empty(self.game.get_board_size())
        y = np.empty(self.game.get_board_size())
        val = np.empty(self.game.get_board_size())
        
        idx = 0
        
        for row in range(self.game.board_h):
            for col in range(self.game.board_w):
                x[idx] = col
                y[col] = row
                val[idx] = self.game.board[col + row * self.game.board_w] + 1
                idx += 1
    
        return np.array([[self.game.board[col + row * self.game.board_w] for col in range(self.game.board_w)] for row in range(self.game.board_h)])
    
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
        print(reward, done)
        return self.obs, reward, done, {}
    
    def render(self, mode):
        if(mode == "human"):
            self.game.print_board()
    
    def reset(self):
        self.actions = 0
        self.game.reset()
        self.obs = self.gen_obs()
        return self.obs

if (__name__ == "__main__"):
    env = minesweep()
    
    
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(255))
    model.add(Activation('relu'))
    nb_actions = env.action_size()
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print(model.summary())
   
    
    policy = EpsGreedyQPolicy()
    sars = SARSAAgent(model=model, nb_actions=nb_actions, nb_steps_warmup=100, policy=policy)
    sars.compile(Adam(lr=1e-3), metrics=['mae'])
    sars.fit(env, nb_steps=5000, visualize=False, verbose=2)
    
    """EXAMPLE:
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    nb_actions = env.action_space.n
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print(model.summary())
    polcy = EpisGreedyQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
    target_model_update=1e-2, policy=policy)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])
    
    # Okay, now it's time to learn something! We visualize the training here for show, but this slows down training quite a lot. 
    dqn.fit(env, nb_steps=5000, visualize=True, verbose=2)
    """
    
    