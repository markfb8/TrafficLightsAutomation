from os.path import exists
from stable_baselines3 import PPO

from Environment import DynamicTrafficControlEnv
from Scheduler import Scheduler


class Program:
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

    def print_statistics(self):
        def calc_waiting_time():
            accumulated_waiting_time = 0
            cars_leaving_simulator = 0

            while not self.scheduler.out.empty():
                accumulated_waiting_time += self.scheduler.out.get().waiting_time
                cars_leaving_simulator += 1

            average_waiting_time = accumulated_waiting_time / cars_leaving_simulator if cars_leaving_simulator > 0 else 'no cars left the simulator'

            return average_waiting_time

        print("\n---- STATISTICS ----")
        print("Cars created: " + str(self.scheduler.cars_created))
        print("Cars eliminated: " + str(self.scheduler.out.qsize()))
        print("Percentage of cars that have crossed the model: " + str(self.scheduler.out.qsize() / self.scheduler.cars_created))
        print("Average waiting time: " + str(calc_waiting_time()))

    def create_scheduler(self):
        self.scheduler = Scheduler(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)

    def train(self):
        env = DynamicTrafficControlEnv(self.rows * self.cols, self.road_length, self.scheduler)

        if exists('models/test.zip'):
            model = PPO.load('models/test', env=env)
        else:
            model = PPO(policy='MultiInputPolicy', env=env, verbose=1)

        while True:
            model.learn(total_timesteps=2024, n_eval_episodes=1)
            model.save('models/test')
            _ = env.reset()

    def predict(self):
        env = DynamicTrafficControlEnv(self.rows * self.cols, self.road_length, self.scheduler)
        model = PPO.load('models/test', env=env)
        observation = env.reset()

        done = False

        while not done:
            action = model.predict(observation)
            observation, rewards, done, info = env.step(action[0])

    def standard(self):
        time_between_changes = int(input('\nTime between changes: '))

        self.scheduler.start_simulation()
        last_time_lights_changed = 0
        done = False

        while not done:
            if (self.scheduler.current_time - last_time_lights_changed) >= time_between_changes:
                action = [1] * self.rows * self.cols
                last_time_lights_changed = self.scheduler.current_time
            else:
                action = [0] * self.rows * self.cols

            done = self.scheduler.advance_step(action)

        self.print_statistics()


if __name__ == '__main__':
    operation = int(input('\nOPERATION TO PERFORM:\n1. Train\n2. Predict\n3. Standard\n'))

    program = Program()
    program.get_data()
    program.create_scheduler()

    if operation == 1:
        program.train()
    elif operation == 2:
        program.predict()
    elif operation == 3:
        program.standard()
