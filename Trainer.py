from stable_baselines3 import PPO
from TrainingEnvironment import DynamicTrafficControlEnv
from TrainingScheduler import Scheduler


class Trainer:
    def __init__(self):
        self.traffic_volume = None
        self.rows = None
        self.cols = None
        self.road_length = None
        self.simulation_time = None
        self.scheduler = None

    def get_data(self):
        self.traffic_volume = int(input('\nTraffic density: (1, 2 o 3):\n1. Low\n2. Medium\n3. High\n'))

        self.rows = int(input('\nCity map size (Rows): '))

        self.cols = int(input('\nCity map size (Columns): '))

        self.road_length = int(input('\nRoad length (number of cars): '))

        self.simulation_time = int(input('\nSimulation time in minutes: ')) * 60

    def create_scheduler(self):
        self.scheduler = Scheduler(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)

    def train(self):
        env = DynamicTrafficControlEnv(self.rows * self.cols, self.road_length, self.simulation_time, self.scheduler)
        model = PPO(policy='MultiInputPolicy', env=env, verbose=1)
        model.learn(total_timesteps=20000)
        # obs = env.reset()


if __name__ == '__main__':
    trainer = Trainer()
    trainer.get_data()
    trainer.create_scheduler()
    trainer.train()
