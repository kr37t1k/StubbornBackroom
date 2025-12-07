import gymnasium
from gymnasium import spaces

class BotEnv(gymnasium.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=0, high=1, shape=(1,))

    def step(self, action):
        if action == 0:
            reward = 0
            done = True
        else:
            reward = 1
            done = False
        return self.observation_space.sample(), reward, done, {}

    def reset(self):
        return self.observation_space.sample()