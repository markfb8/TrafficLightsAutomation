import gym
from gym import spaces
import numpy as np

from TrainingScheduler import TrainingScheduler


class DynamicTrafficControlEnv(gym.Env):
    def __init__(self, num_intersections, road_length, scheduler: TrainingScheduler):
        self.scheduler = scheduler
        super(DynamicTrafficControlEnv, self).__init__()

        self.action_space = spaces.Box(np.zeros(num_intersections), np.ones(num_intersections), dtype=np.uint8)
        self.observation_space = spaces.Dict({
            "lights_settings": spaces.Box(low=-5, high=5, shape=(1, num_intersections), dtype=np.uint8),
            "horizontal_num_of_cars": spaces.Box(low=0, high=road_length, shape=(1, num_intersections), dtype=np.uint8),
            "vertical_num_of_cars": spaces.Box(low=0, high=road_length, shape=(1, num_intersections), dtype=np.uint8),
            "horizontal_waiting_time": spaces.Box(low=0, high=65535, shape=(num_intersections, road_length), dtype=np.uint8),
            "vertical_waiting_time": spaces.Box(low=0, high=65535, shape=(num_intersections, road_length), dtype=np.uint8)
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

        return observation, reward, done, {}

    def render(self, mode='human', close=False):
        pass
