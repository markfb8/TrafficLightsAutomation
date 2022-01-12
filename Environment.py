import gym
from gym import spaces
import numpy as np
import learning_data

from Simulation import Simulation


class Environment(gym.Env):
    def __init__(self, simulation):
        super(Environment, self).__init__()
        self.simulation = simulation

        self.action_space = spaces.Box(np.zeros(self.simulation.rows * self.simulation.cols), np.ones(self.simulation.rows * self.simulation.cols), dtype=np.uint8)
        self.observation_space = spaces.Dict({
            "lights_settings": spaces.Box(low=0, high=1, shape=(1, self.simulation.rows * self.simulation.cols), dtype=np.uint8),
            "horizontal_num_of_cars": spaces.Box(low=0, high=self.simulation.road_length, shape=(1, self.simulation.rows * self.simulation.cols), dtype=np.uint8),
            "vertical_num_of_cars": spaces.Box(low=0, high=self.simulation.road_length, shape=(1, self.simulation.rows * self.simulation.cols), dtype=np.uint8),
            "horizontal_waiting_time": spaces.Box(low=-1, high=65535, shape=(self.simulation.rows * self.simulation.cols, self.simulation.road_length), dtype=np.int32),
            "vertical_waiting_time": spaces.Box(low=-1, high=65535, shape=(self.simulation.rows * self.simulation.cols, self.simulation.road_length), dtype=np.int32)
        })

    def reset(self, reset_simulation=True):
        print('\033[94m' + 'resetting environment...' + '\033[0;0m')
        if reset_simulation:
            self.simulation = Simulation(self.simulation.traffic_volume, self.simulation.rows, self.simulation.cols, self.simulation.road_length, self.simulation.simulation_time)
        observation = self.simulation.get_observation()
        learning_data.previous_observation = observation

        return observation

    def step(self, action):
        previous_observation = learning_data.previous_observation
        done = self.simulation.advance_step(action, False)
        current_observation = self.simulation.get_observation()
        learning_data.previous_observation = current_observation

        reward = self.reward_function_1(previous_observation, current_observation)

        return current_observation, reward, done, {}

    def render(self, mode='human', close=False):
        pass

    def reward_function_1(self, previous_observation, current_observation):
        previous_horizontal_waiting_time = 0
        previous_vertical_waiting_time = 0
        current_horizontal_waiting_time = 0
        current_vertical_waiting_time = 0
        for intersection in range(self.simulation.rows * self.simulation.cols):
            for car in range(self.simulation.road_length):
                if previous_observation['horizontal_waiting_time'][intersection][car] != -1:
                    previous_horizontal_waiting_time += previous_observation['horizontal_waiting_time'][intersection][car]
                if previous_observation['vertical_waiting_time'][intersection][car] != -1:
                    previous_vertical_waiting_time += previous_observation['vertical_waiting_time'][intersection][car]
                if current_observation['horizontal_waiting_time'][intersection][car] != -1:
                    current_horizontal_waiting_time += current_observation['horizontal_waiting_time'][intersection][car]
                if current_observation['vertical_waiting_time'][intersection][car] != -1:
                    current_vertical_waiting_time += current_observation['vertical_waiting_time'][intersection][car]

        previous_waiting_time = previous_horizontal_waiting_time + previous_vertical_waiting_time
        current_waiting_time = current_horizontal_waiting_time + current_vertical_waiting_time

        return previous_waiting_time - current_waiting_time

    def reward_function_2(self, previous_observation, action):
        reward = 0

        num_of_intersections = self.simulation.rows * self.simulation.cols
        for intersection in range(num_of_intersections):
            # If the vertical lights turn green
            if previous_observation['lights_settings'] == 1 and action[intersection] == 1:
                reward = reward + previous_observation['vertical_num_of_cars'][intersection] - previous_observation['horizontal_num_of_cars'][intersection]
            # If the horizontal lights turn green
            elif previous_observation['lights_settings'] == 0 and action[intersection] == 1:
                reward = reward + previous_observation['horizontal_num_of_cars'][intersection] - previous_observation['vertical_num_of_cars'][intersection]

        return reward

    def reward_function_3(self, previous_observation, action):
        reward = 0

        num_of_intersections = self.simulation.rows * self.simulation.cols
        for intersection in range(num_of_intersections):
            # If the vertical lights turn green
            if previous_observation['lights_settings'] == 1 and action[intersection] == 1:
                for car in range(self.simulation.road_length):
                    if previous_observation['vertical_waiting_time'][intersection][car] != -1:
                        reward += previous_observation['vertical_waiting_time'][intersection][car]
                    if previous_observation['horizontal_waiting_time'][intersection][car] != -1:
                        reward -= previous_observation['horizontal_waiting_time'][intersection][car]

            # If the horizontal lights turn green
            if previous_observation['lights_settings'] == 0 and action[intersection] == 1:
                for car in range(self.simulation.road_length):
                    if previous_observation['horizontal_waiting_time'][intersection][car] != -1:
                        reward += previous_observation['horizontal_waiting_time'][intersection][car]
                    if previous_observation['vertical_waiting_time'][intersection][car] != -1:
                        reward -= previous_observation['vertical_waiting_time'][intersection][car]

        return reward

    def reward_function_4(self, previous_observation, action):
        reward = 0

        num_of_intersections = self.simulation.rows * self.simulation.cols
        for intersection in range(num_of_intersections):
            # If the vertical lights turn green
            if previous_observation['lights_settings'] == 1 and action[intersection] == 1:
                if previous_observation['vertical_waiting_time'][intersection][0] != -1:
                    reward += previous_observation['vertical_waiting_time'][intersection][0]
                if previous_observation['horizontal_waiting_time'][intersection][0] != -1:
                    reward -= previous_observation['horizontal_waiting_time'][intersection][0]

            # If the horizontal lights turn green
            if previous_observation['lights_settings'] == 0 and action[intersection] == 1:
                if previous_observation['horizontal_waiting_time'][intersection][0] != -1:
                    reward += previous_observation['horizontal_waiting_time'][intersection][0]
                if previous_observation['vertical_waiting_time'][intersection][0] != -1:
                    reward -= previous_observation['vertical_waiting_time'][intersection][0]

        return reward

    def reward_function_5(self, previous_observation, action, current_observation):
        return previous_observation['average_waiting_time'][0] - current_observation['average_waiting_time'][0]
