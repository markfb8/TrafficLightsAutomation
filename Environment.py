import gym
from gym import spaces
import numpy as np
import learning_data

from Simulation import Simulation


class Environment(gym.Env):
    def __init__(self, simulation, training):
        super(Environment, self).__init__()
        self.simulation = simulation
        self.training = training

        self.action_space = spaces.Discrete(self.simulation.rows * self.simulation.cols * 2)
        self.observation_space = spaces.Dict({
            'current_time': spaces.Box(low=0, high=2147483647, shape=(1,), dtype=np.int32),
            # 'average_waiting_time': spaces.Box(low=0, high=2147483647, shape=(1,), dtype=np.int32),
            'lights_settings': spaces.Box(low=0, high=1, shape=(self.simulation.rows * self.simulation.cols,), dtype=np.uint8),
            'ready_to_switch': spaces.Box(low=0, high=1, shape=(self.simulation.rows * self.simulation.cols,), dtype=np.uint8),
            'horizontal_num_of_cars_waiting': spaces.Box(low=0, high=self.simulation.road_length, shape=(self.simulation.rows * self.simulation.cols,), dtype=np.uint8),
            'vertical_num_of_cars_waiting': spaces.Box(low=0, high=self.simulation.road_length, shape=(self.simulation.rows * self.simulation.cols,), dtype=np.uint8)
            # 'horizontal_waiting_time': spaces.Box(low=-1, high=65535, shape=(self.simulation.rows * self.simulation.cols, 1000), dtype=np.int32),
            # 'vertical_waiting_time': spaces.Box(low=-1, high=65535, shape=(self.simulation.rows * self.simulation.cols, 1000), dtype=np.int32)
        })

    def reset(self, reset_simulation=True):
        print('\033[94m' + 'resetting environment...' + '\033[0;0m')
        if reset_simulation:
            self.simulation = Simulation(self.simulation.traffic_volume, self.simulation.rows, self.simulation.cols, self.simulation.road_length, self.simulation.simulation_time)
        observation = self.simulation.get_observation()
        learning_data.previous_observation = observation

        return observation

    def step(self, action):
        if self.training:
            previous_observation = learning_data.previous_observation
            done = self.simulation.advance_step(action)
            current_observation = self.simulation.get_observation()
            learning_data.previous_observation = current_observation

            reward = self.reward_function_7(previous_observation, action)
        else:
            done = self.simulation.advance_step(action)
            current_observation = self.simulation.get_observation()
            reward = 0

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
            if previous_observation['lights_settings'][intersection] == 1 and action[intersection] >= 0.5:
                reward = reward + previous_observation['vertical_num_of_cars_waiting'][intersection] - previous_observation['horizontal_num_of_cars_waiting'][intersection]
            # If the horizontal lights turn green
            elif previous_observation['lights_settings'][intersection] == 0 and action[intersection] >= 0.5:
                reward = reward + previous_observation['horizontal_num_of_cars_waiting'][intersection] - previous_observation['vertical_num_of_cars_waiting'][intersection]

        return reward

    def reward_function_3(self, previous_observation, action):
        reward = 0

        num_of_intersections = self.simulation.rows * self.simulation.cols
        for intersection in range(num_of_intersections):
            # If the vertical lights turn green
            if previous_observation['lights_settings'][intersection] >= 1 and action[intersection] >= 0.5:
                for car in range(self.simulation.road_length):
                    if previous_observation['vertical_waiting_time'][intersection][car] != -1:
                        reward += previous_observation['vertical_waiting_time'][intersection][car]
                    if previous_observation['horizontal_waiting_time'][intersection][car] != -1:
                        reward -= previous_observation['horizontal_waiting_time'][intersection][car]

            # If the horizontal lights turn green
            if previous_observation['lights_settings'][intersection] == 0 and action[intersection] >= 0.5:
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
            if previous_observation['lights_settings'][intersection] == 1 and action[intersection] == 1:
                if previous_observation['vertical_waiting_time'][intersection][0] != -1:
                    reward += previous_observation['vertical_waiting_time'][intersection][0]
                if previous_observation['horizontal_waiting_time'][intersection][0] != -1:
                    reward -= previous_observation['horizontal_waiting_time'][intersection][0]

            # If the horizontal lights turn green
            if previous_observation['lights_settings'][intersection] == 0 and action[intersection] == 1:
                if previous_observation['horizontal_waiting_time'][intersection][0] != -1:
                    reward += previous_observation['horizontal_waiting_time'][intersection][0]
                if previous_observation['vertical_waiting_time'][intersection][0] != -1:
                    reward -= previous_observation['vertical_waiting_time'][intersection][0]

        return reward

    def reward_function_5(self, previous_observation, current_observation):
        return previous_observation['average_waiting_time'] - current_observation['average_waiting_time']

    def reward_function_6(self, previous_observation, action):
        reward = 0

        if action < self.simulation.rows * self.simulation.cols:
            if previous_observation['ready_to_switch'][action] == 0:
                reward -= 1

        return reward

    def reward_function_7(self, previous_observation, action):
        reward = 0

        if action < self.simulation.rows * self.simulation.cols:
            if previous_observation['lights_settings'][action] == 1:
                reward += (previous_observation['vertical_num_of_cars_waiting'][action] - previous_observation['horizontal_num_of_cars_waiting'][action]) / self.simulation.road_length
            else:
                reward += (previous_observation['horizontal_num_of_cars_waiting'][action] - previous_observation['vertical_num_of_cars_waiting'][action]) / self.simulation.road_length
            if previous_observation['ready_to_switch'][action] == 0:
                reward -= 1

        # for intersection in range(self.simulation.rows * self.simulation.cols):
        #    if intersection != action:

        return reward
