import sys
from os.path import exists
from stable_baselines3 import PPO

from Environment import Environment
from Simulation import Simulation


class Program:
    def __init__(self):
        self.operation = int(input('\nOPERATION TO PERFORM:\n1. Train\n2. Predict\n3. Standard\n4. Standard range\n'))
        self.traffic_volume = int(input('\nTraffic density: (1, 2 o 3):\n1. Low\n2. Medium\n3. High\n'))

        if self.operation != 2:
            self.rows = int(input('\nCity map size (Rows): '))
            self.cols = int(input('\nCity map size (Columns): '))
            self.road_length = int(input('\nRoad length (number of cars): '))

        if self.operation == 1:
            self.simulation_time = sys.maxsize
            self.model_name = input('\nModel name: ')
            self.train()
        elif self.operation == 2:
            self.simulation_time = int(input('\nSimulation duration in minutes: ')) * 60
            self.model_name = input('\nModel name: ')
            self.predict()
        elif self.operation == 3:
            self.simulation_time = int(input('\nSimulation duration in minutes: ')) * 60
            self.time_between_changes = int(input('\nTime between changes: '))
            self.standard()
        elif self.operation == 4:
            self.simulation_time = int(input('\nSimulation duration in minutes: ')) * 60
            self.time_between_changes = int(input('\nTime between changes start: '))
            self.time_between_changes_end = int(input('\nTime between changes end: '))
            self.standard_range()

        # self.simulation = Simulation(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)
        self.simulation = None

    def print_statistics(self, title):
        average_waiting_time, cars_leaving_simulator = self.simulation.get_average_waiting_time()
        self.simulation.get_average_waiting_time()

        print('\n\033[94m' + title + '\033[35m')
        print("Cars created: " + str(self.simulation.cars_created))
        print("Cars eliminated: " + str(cars_leaving_simulator))
        print("Percentage of cars that have crossed the model: " + str(cars_leaving_simulator / self.simulation.cars_created))
        print("Average waiting time: " + str(average_waiting_time))
        print('\033[0;0m')

    def train(self):
        self.simulation = Simulation(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)

        model_info = open('./models/' + self.model_name + '.info', 'w')
        model_info.write(str(self.rows) + '\n' + str(self.cols) + '\n' + str(self.road_length))
        model_info.close()

        env = Environment(self.simulation)

        if exists('models/' + self.model_name + '.zip'):
            model = PPO.load('models/' + self.model_name, env=env)
        else:
            model = PPO(policy='MultiInputPolicy', env=env, verbose=1)

        while True:
            model.learn(total_timesteps=10240, n_eval_episodes=5)
            model.save('models/' + self.model_name)

    def predict(self):
        model_info = open('./models/' + self.model_name + '.info', 'r')
        lines = model_info.readlines()
        self.rows = int(lines[0])
        self.cols = int(lines[1])
        self.road_length = int(lines[2])

        self.simulation = Simulation(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)

        env = Environment(self.simulation)
        model = PPO.load('models/' + self.model_name, env=env)
        observation = env.reset(False)

        done = False
        while not done:
            action = model.predict(observation)
            observation, _, done, _ = env.step(action[0])

        self.print_statistics('Statistics:')

    def standard(self, additional_statistics_text=''):
        self.simulation = Simulation(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)

        last_time_lights_changed = 0
        done = False
        while not done:
            if (self.simulation.current_time - last_time_lights_changed) >= self.time_between_changes:
                last_time_lights_changed = self.simulation.current_time
                done = self.simulation.advance_step([1] * self.rows * self.cols, True)
            else:
                done = self.simulation.advance_step([0] * self.rows * self.cols, True)

        self.print_statistics('Statistics' + additional_statistics_text + ':')

    def standard_range(self):
        standard_info = open('./data/standard_info.txt', 'w')
        switch_intervals = open('./data/switch_intervals.txt', 'w')
        average_waiting_times = open('./data/average_waiting_times.txt', 'w')

        while self.time_between_changes <= self.time_between_changes_end:
            self.standard('(Current time between changes is ' + str(self.time_between_changes) + ')')

            standard_info.write(str(self.time_between_changes) + ' ' + str(self.simulation.get_average_waiting_time()[0]) + '\n')
            switch_intervals.write(str(self.time_between_changes) + '\n')
            average_waiting_times.write(str(self.simulation.get_average_waiting_time()[0]) + '\n')
            self.time_between_changes += 1

        standard_info.close()


if __name__ == '__main__':
    program = Program()
