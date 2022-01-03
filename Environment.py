import gym
from gym import spaces
import numpy as np

from Simulation import Simulation


class DynamicTrafficControlEnv(gym.Env):
    def __init__(self, num_intersections, road_length, simulation: Simulation):
        self.simulation = simulation
        super(DynamicTrafficControlEnv, self).__init__()

        self.action_space = spaces.Box(np.zeros(num_intersections), np.ones(num_intersections), dtype=np.uint8)
        self.observation_space = spaces.Dict({
            "lights_settings": spaces.Box(low=-3, high=3, shape=(1, num_intersections), dtype=np.uint8),
            "horizontal_num_of_cars": spaces.Box(low=0, high=road_length, shape=(1, num_intersections), dtype=np.uint8),
            "vertical_num_of_cars": spaces.Box(low=0, high=road_length, shape=(1, num_intersections), dtype=np.uint8),
            "horizontal_waiting_time": spaces.Box(low=-1, high=65535, shape=(num_intersections, road_length), dtype=np.int32),
            "vertical_waiting_time": spaces.Box(low=-1, high=65535, shape=(num_intersections, road_length), dtype=np.int32)
        })

    def reset(self):
        self.simulation.start_simulation()
        observation = self.simulation.get_observation()

        return observation

    def step(self, action):
        observation = self.simulation.get_observation()
        done = self.simulation.advance_step(action)
        reward = 0

        if done:
            self.reset()

        return observation, reward, done, {}

    def render(self, mode='human', close=False):
        pass
