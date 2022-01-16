import gym
from gym import spaces
import numpy as np
import learning_data

from Simulation import Simulation


def get_value_or_delimiter(value, delimiter):
    return min(delimiter[1], max(delimiter[0], value))


class Environment(gym.Env):
    def __init__(self, simulation, training):
        super(Environment, self).__init__()
        self.simulation = simulation
        self.training = training

        self.action_space = spaces.Discrete(2)
        observation_space_dictionary = dict()
        observation_space_dictionary['lights_settings'] = spaces.Box(low=0, high=1, shape=(1,), dtype=np.uint8)
        observation_space_dictionary['intersection_cars'] = spaces.Box(low=0, high=1000, shape=(2,), dtype=np.uint8)
        observation_space_dictionary['input_cars'] = spaces.Box(low=0, high=1000, shape=(2,), dtype=np.uint8)
        observation_space_dictionary['output_cars'] = spaces.Box(low=0, high=1000, shape=(2,), dtype=np.uint8)
        self.observation_space = spaces.Dict(observation_space_dictionary)

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

            reward = self.definitive2x2(previous_observation, action)
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

    def reward_function_6(self, current_observation):
        return - current_observation['average_waiting_time'][0]

    def reward_function_7(self, previous_observation, action):
        reward = 0

        if action < self.simulation.rows * self.simulation.cols:
            if previous_observation['ready_to_switch'][action] == 0:
                reward -= 1

        return reward

    def reward_function_8(self, previous_observation, action):
        reward = 0

        if action < self.simulation.rows * self.simulation.cols:
            if previous_observation['lights_settings'][action] == 1:
                reward += (previous_observation['vertical_num_of_cars_waiting'][action] - previous_observation['horizontal_num_of_cars_waiting'][action]) / self.simulation.road_length
            else:
                reward += (previous_observation['horizontal_num_of_cars_waiting'][action] - previous_observation['vertical_num_of_cars_waiting'][action]) / self.simulation.road_length
            if previous_observation['ready_to_switch'][action] == 0:
                reward -= 1

        return reward

    def reward_function_9(self, previous_observation, action):
        reward = -4

        if action < self.simulation.rows * self.simulation.cols:
            if previous_observation['lights_settings'][action] == 1:
                reward += previous_observation['vertical_num_of_cars_waiting'][action] - previous_observation['horizontal_num_of_cars_waiting'][action]
            else:
                reward += previous_observation['horizontal_num_of_cars_waiting'][action] - previous_observation['vertical_num_of_cars_waiting'][action]
        return reward

    def reward_function_10(self, previous_observation, action):
        if action < self.simulation.rows * self.simulation.cols:
            # print('vertical cars: ' + str(previous_observation['vertical_num_of_cars'][action]), 'horizontal cars: ' + str(previous_observation['horizontal_num_of_cars'][action]))

            # reward = -10 if previous_observation['ready_to_switch'][action] == 0 else 0
            reward = - self.simulation.road_length / 2

            if previous_observation['lights_settings'][action] == 1:
                reward += min(previous_observation['vertical_num_of_cars'][action] - previous_observation['horizontal_num_of_cars'][action], self.simulation.road_length)
            else:
                reward += min(previous_observation['horizontal_num_of_cars'][action] - previous_observation['vertical_num_of_cars'][action], self.simulation.road_length)
        else:
            reward = 0

            not_action = action - self.simulation.rows * self.simulation.cols

            if previous_observation['lights_settings'][not_action] == 1:
                reward += max(previous_observation['horizontal_num_of_cars'][not_action] - previous_observation['vertical_num_of_cars'][not_action], - self.simulation.road_length)
            else:
                reward += max(previous_observation['vertical_num_of_cars'][not_action] - previous_observation['horizontal_num_of_cars'][not_action], - self.simulation.road_length)

        # print('action: ' + str(action) + ', reward: ' + str(reward))

        return reward

    def reward_function_11(self, prev_obs, action):
        reward = 0
        if action == 1:
            reward = - self.simulation.road_length
            if prev_obs['lights_settings'][0] == 1:
                reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][0] - prev_obs['num_of_cars'][0][1], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][0] - prev_obs['num_of_cars'][1][0], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=- prev_obs['num_of_cars'][0][1] + self.simulation.road_length, delimiter=[-self.simulation.road_length, 0])
            else:
                reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][1] - prev_obs['num_of_cars'][0][0], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][1] - prev_obs['num_of_cars'][1][1], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=- prev_obs['num_of_cars'][0][0] + self.simulation.road_length, delimiter=[-self.simulation.road_length, 0])
        else:
            if prev_obs['lights_settings'][0] == 0:
                reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][0] - prev_obs['num_of_cars'][0][1], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][0] - prev_obs['num_of_cars'][1][0], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=- prev_obs['num_of_cars'][0][0] + self.simulation.road_length, delimiter=[-self.simulation.road_length, 0])
            else:
                reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][1] - prev_obs['num_of_cars'][0][0], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=prev_obs['num_of_cars'][0][1] - prev_obs['num_of_cars'][1][1], delimiter=[-self.simulation.road_length, self.simulation.road_length])
                # reward += get_value_or_delimiter(value=- prev_obs['num_of_cars'][0][1] + self.simulation.road_length, delimiter=[-self.simulation.road_length, 0])

        # print('action: ' + str(action) + ', reward: ' + str(reward))
        # print('vertical cars: ' + str(prev_obs['num_of_cars'][0][0]), 'horizontal cars: ' + str(prev_obs['num_of_cars'][0][1]) + '\n')

        return reward

    def reward_function_12(self, prev_obs, action):
        reward = 0
        if prev_obs['ready_to_switch'] == 0:
            if action == 1:
                reward = -10
        else:
            if action == 1:
                if prev_obs['lights_settings'][0] == 1:
                    reward += 1 if prev_obs['num_of_cars'][0][0] > 8 and prev_obs['num_of_cars'][0][1] < 2 else 0
                    # reward += 1 if prev_obs['num_of_cars'][1][0] < 2 else 0
                else:
                    reward += 1 if prev_obs['num_of_cars'][0][1] > 8 and prev_obs['num_of_cars'][0][0] < 2 else 0
                    # reward += 1 if prev_obs['num_of_cars'][2][1] < 2 else 0
            else:
                if prev_obs['lights_settings'][0] == 0:
                    reward += 1 if prev_obs['num_of_cars'][0][0] > 8 else 0
                else:
                    reward += 1 if prev_obs['num_of_cars'][0][1] > 8 else 0

            # if self.simulation.intersection_to_process == 2:
            # print('action: ' + str(action) + ', reward: ' + str(reward))
            # print('vertical cars: ' + str(prev_obs['num_of_cars'][0][0]), 'horizontal cars: ' + str(prev_obs['num_of_cars'][0][1]) + '\n')

        return reward

    def definitive2x2(self, prev_obs, action):
        reward = 0

        vertical_load = prev_obs['intersection_cars'][0]  # + prev_obs['input_cars'][0]
        horizontal_load = prev_obs['intersection_cars'][1]  # + prev_obs['input_cars'][1]

        if prev_obs['lights_settings'][0] == 0:
            if horizontal_load > 2 * vertical_load:
                if action == 1:
                    reward = 1
                else:
                    reward = -1
            elif vertical_load > 2 * horizontal_load:
                if action == 1:
                    reward = -1
                else:
                    reward = 1
            elif action == 1:
                reward = -1
        if prev_obs['lights_settings'][0] == 1:
            if horizontal_load > 2 * vertical_load:
                if action == 1:
                    reward = -1
                else:
                    reward = 1
            elif vertical_load > 2 * horizontal_load:
                if action == 1:
                    reward = 1
                else:
                    reward = -1
            elif action == 1:
                reward = -1

        if self.simulation.intersection_to_process == 20:
            print('The vertical load is: ' + str(vertical_load))
            print('The horizontal load is: ' + str(horizontal_load))
            print('The green light is: ' + str('VERTICAL' if prev_obs['lights_settings'][0] == 0 else 'HORIZONTAL'))
            print('The action is: ' + str('MAINTAIN' if action == 0 else 'CHANGE'))
            print('The reward is: ' + str(reward))
            print('\n')

        return reward

    def definitive3x3(self, prev_obs, action):
        reward = 0

        vertical_load = prev_obs['intersection_cars'][0]
        horizontal_load = prev_obs['intersection_cars'][1]
        vertical_output_load = prev_obs['output_cars'][0]
        horizontal_output_load = prev_obs['output_cars'][1]

        if prev_obs['lights_settings'][0] == 0:
            if horizontal_load - vertical_load > 6:
                reward = 1 if action == 1 else -1
            elif vertical_load - horizontal_load > 4:
                reward = -1 if action == 1 else 1

            elif vertical_output_load - horizontal_output_load > 6:
                reward = 1 if action == 1 else -1
            elif horizontal_output_load - vertical_output_load > 4:
                reward = -1 if action == 1 else 1

            elif vertical_load > 5 and horizontal_load > 5 and vertical_output_load - horizontal_output_load > 3:
                reward = 1 if action == 1 else -1

            elif vertical_output_load == 10:
                reward = 1 if action == 1 else -1

            elif action == 1:
                reward = -1

        if prev_obs['lights_settings'][0] == 1:
            if vertical_load - horizontal_load > 6:
                reward = 1 if action == 1 else -1
            elif horizontal_load - vertical_load > 4:
                reward = -1 if action == 1 else 1

            elif horizontal_output_load - vertical_output_load > 6:
                reward = 1 if action == 1 else -1
            elif vertical_output_load - horizontal_output_load > 4:
                reward = -1 if action == 1 else 1

            elif horizontal_load > 5 and vertical_load > 5 and horizontal_output_load - vertical_output_load > 3:
                reward = 1 if action == 1 else -1

            elif horizontal_output_load == 10:
                reward = 1 if action == 1 else -1

            elif action == 1:
                reward = -1

            print('The intersection is: ' + str(self.simulation.intersection_to_process))
            print('The vertical load is: ' + str(vertical_load))
            print('The horizontal load is: ' + str(horizontal_load))
            print('The vertical output load is: ' + str(vertical_output_load))
            print('The horizontal output load is: ' + str(horizontal_output_load))
            print('The green light is: ' + str('VERTICAL' if prev_obs['lights_settings'][0] == 0 else 'HORIZONTAL'))
            print('The action is: ' + str('MAINTAIN' if action == 0 else 'CHANGE'))
            print('The reward is: ' + str(reward))
            print('\n')

        return reward
