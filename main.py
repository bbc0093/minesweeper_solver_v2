import numpy as np
import gym
from gym import spaces

#from parse_game import game
from minesweeper import game
from analyze_progress import plot_results

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.sarsa import SARSAAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

import datetime
import pickle

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
        
        self.runs = 0
        self.wins = 0
        self.loses = 0
        
        self.eps_dups = 0
        self.dups = []
        self.results = []
        self.clicks = []
        self.total_rewards = []
        self.avg_rewards = []
        self.eps_rewards = []
        
        self.win_reward = (self.game.board_w-1)*(self.game.board_h-1)*100
        self.lose_reward = -(self.game.board_w-1)*(self.game.board_h-1)
        self.rep_reward = -10
        
        self.reward_range = (min(self.rep_reward, self.lose_reward), self.win_reward, np.int64)
        
        self.action_space = spaces.Discrete(self.action_size())
        
        #-1 is unknown 0-8 are num values, 9 is known bomb
        self.observation_space = spaces.Box(-1, 9, (self.game.board_w, self.game.board_h))   #X, Y, val
    
    def _take_action(self, action):
        rl = action > (self.game.board_w * self.game.board_h)
        if(rl):
            action -= self.game.board_w * self.game.board_h     
        
        x = int(action % self.game.board_w)
        action /= self.game.board_w
        
        y = int(action)
        

        if(not self.game.is_valid_loc(x, y)):
            return 1

        if(rl):
            self.game.right_click(x, y)
        else:
            self.game.click(x, y)
            
        self.game.update_board()
    
    def obs_size(self):
        return self.game.board_w * self.game.board_h * 10
    
    def action_size(self):
        # One action per board position * R/L: Click
        # return self.game.board_w * self.game.board_h * 2
        # only left clicks for now
        return self.game.board_w * self.game.board_h 
    
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
            reward =  self.rep_reward
            self.eps_dups += 1
            done = 0
        elif(not self.game.result):
            done = 0
            reward = self.game.num_clicks()
        elif(self.game.result == "won"):
            self.results.append("W")
            self.wins += 1
            done = 1
            reward = self.win_reward
        elif(self.game.result == "lost"):
            self.loses += 1
            self.results.append("L")
            done = 1
            reward = self.lose_reward
            
        self.obs = self.gen_obs()
        
        print(reward)
        self.eps_rewards.append(reward)
        
        return self.obs, reward, done, {}
    
    def render(self, mode):
        if(mode == "human"):
            self.game.print_board()
    
    def reset(self):
        if len(self.eps_rewards) != 0:  #check for start reset and prevent dvd by 0 error
            self.clicks.append(self.game.num_clicks())
            self.dups.append(self.eps_dups)
            self.eps_dups = 0
            self.total_rewards.append(sum(self.eps_rewards))
            self.avg_rewards.append(sum(self.eps_rewards)/len(self.eps_rewards))
            self.eps_rewards = []
        
        self.runs += 1
        self.game.reset()
        self.obs = self.gen_obs()
        return self.obs
    
    def record(self):
        return "W: {}, L: {}, R: {}".format(self.wins, self.loses, self.runs)

    def plot_results(self):   
        pickle.dump([self.total_rewards, self.avg_rewards, self.results, self.clicks, self.dups], open("data.p", "wb+"))
        plot_results(self.total_rewards, self.avg_rewards, self.results, self.clicks, self.dups)
        


if (__name__ == "__main__"):
    width = 255
    depth = 100
    
    env = minesweep()
    
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    
    for _ in range(depth):
        model.add(Dense(width))
        model.add(Activation('relu'))

    nb_actions = env.action_size()
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print(model.summary())
   
    
    policy = EpsGreedyQPolicy()
    sars = SARSAAgent(model=model, nb_actions=nb_actions, nb_steps_warmup=1000, policy=policy, gamma = .999)
    sars.compile(Adam(lr=1e-3), metrics=['mae'])
    sars.fit(env, nb_steps=500*1000, visualize=False, verbose=2)
    
    cur_time = datetime.datetime.now()
    filename = 'weights/sarsa_minesweeper_weights_{}.h5f'.format(cur_time.strftime("%m-%d-%Y--%H-%M-%S"))
    sars.save_weights(filename, overwrite=True)

    
    print(env.record())
    env.plot_results()
    
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
    
    