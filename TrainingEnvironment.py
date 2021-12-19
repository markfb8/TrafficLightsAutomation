import gym
from gym import spaces
import numpy as np

from TrainingScheduler import Scheduler


class DynamicTrafficControlEnv(gym.Env):
    def __init__(self, num_intersections, max_cars_in_road, simulation_time, scheduler: Scheduler):
        self.scheduler = scheduler
        super(DynamicTrafficControlEnv, self).__init__()

        self.action_space = spaces.Discrete(num_intersections)
        self.observation_space = spaces.Dict({
            "lights_setting": spaces.Discrete(num_intersections),
            "horizontal_num_of_cars": spaces.Box(low=0, high=max_cars_in_road, shape=(1, num_intersections), dtype=np.uint8),
            "vertical_num_of_cars": spaces.Box(low=0, high=max_cars_in_road, shape=(1, num_intersections), dtype=np.uint8),
            "horizontal_waiting_time": spaces.Box(low=0, high=simulation_time, shape=(num_intersections, max_cars_in_road), dtype=np.uint8),
            "vertical_waiting_time": spaces.Box(low=0, high=simulation_time, shape=(num_intersections, max_cars_in_road), dtype=np.uint8)
        })

    def reset(self):
        self.scheduler.start_simulation()
        observation = self.scheduler.get_observation()

        return observation

    def step(self, action):
        observation = self.scheduler.get_observation()
        done = self.scheduler.advance_step(action)
        reward = 0

        if done:
            self.reset()

        return observation, reward, done

    def render(self, mode='human', close=False):
        pass
