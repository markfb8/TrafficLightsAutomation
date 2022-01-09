import gym
from gym import spaces
import numpy as np
import learning_data

from Simulation import Simulation


class DynamicTrafficControlEnv(gym.Env):
    def __init__(self, simulation: Simulation):
        self.simulation = simulation
        super(DynamicTrafficControlEnv, self).__init__()

        self.action_space = spaces.Box(np.zeros(simulation.rows * simulation.cols), np.ones(simulation.rows * simulation.cols), dtype=np.uint8)
        self.observation_space = spaces.Dict({
            "lights_settings": spaces.Box(low=0, high=1, shape=(1, simulation.rows * simulation.cols), dtype=np.uint8),
            "horizontal_num_of_cars": spaces.Box(low=0, high=simulation.road_length, shape=(1, simulation.rows * simulation.cols), dtype=np.uint8),
            "vertical_num_of_cars": spaces.Box(low=0, high=simulation.road_length, shape=(1, simulation.rows * simulation.cols), dtype=np.uint8),
            "horizontal_waiting_time": spaces.Box(low=-1, high=65535, shape=(simulation.rows * simulation.cols, simulation.road_length), dtype=np.int32),
            "vertical_waiting_time": spaces.Box(low=-1, high=65535, shape=(simulation.rows * simulation.cols, simulation.road_length), dtype=np.int32)
        })

    def reset(self):
        self.simulation.start_simulation()
        observation = self.simulation.get_observation()
        learning_data.previous_observation = observation

        return observation

    def step(self, action):
        previous_observation = learning_data.previous_observation
        done = self.simulation.advance_step(action)
        current_observation = self.simulation.get_observation()
        learning_data.previous_observation = current_observation

        reward = self.reward_function_1(previous_observation, current_observation)

        if done:
            self.reset()

        return current_observation, reward, done, {}

    def render(self, mode='human', close=False):
        pass

    def reward_function_1(self, previous_observation, current_observation):
        previous_horizontal_waiting_time = 0
        previous_vertical_waiting_time = 0
        current_horizontal_waiting_time = 0
        current_vertical_waiting_time = 0
        for i in range(self.simulation.rows * self.simulation.cols):
            for j in range(self.simulation.road_length):
                if previous_observation['horizontal_waiting_time'][i][j] != -1:
                    previous_horizontal_waiting_time += previous_observation['horizontal_waiting_time'][i][j]
                if previous_observation['vertical_waiting_time'][i][j] != -1:
                    previous_vertical_waiting_time += previous_observation['vertical_waiting_time'][i][j]
                if current_observation['horizontal_waiting_time'][i][j] != -1:
                    current_horizontal_waiting_time += current_observation['horizontal_waiting_time'][i][j]
                if current_observation['vertical_waiting_time'][i][j] != -1:
                    current_vertical_waiting_time += current_observation['vertical_waiting_time'][i][j]

        previous_waiting_time = previous_horizontal_waiting_time + previous_vertical_waiting_time
        current_waiting_time = current_horizontal_waiting_time + current_vertical_waiting_time

        return previous_waiting_time - current_waiting_time
