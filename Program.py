import sys
from os.path import exists
from stable_baselines3 import PPO

from Environment import DynamicTrafficControlEnv
from Simulation import Simulation


class Program:
    def __init__(self):
        self.operation = int(input('\nOPERATION TO PERFORM:\n1. Train\n2. Predict\n3. Standard\n'))
        self.traffic_volume = int(input('\nTraffic density: (1, 2 o 3):\n1. Low\n2. Medium\n3. High\n'))
        self.rows = int(input('\nCity map size (Rows): '))
        self.cols = int(input('\nCity map size (Columns): '))
        self.road_length = int(input('\nRoad length (number of cars): '))

        if self.operation == 1:
            self.simulation_time = sys.maxsize
            self.model_name = input('\nModel name: ')
        elif self.operation == 2:
            self.simulation_time = int(input('\nSimulation duration in minutes: ')) * 60
            self.model_name = input('\nModel name: ')
        elif self.operation == 3:
            self.simulation_time = int(input('\nSimulation duration in minutes: ')) * 60
            self.time_between_changes = int(input('\nTime between changes: '))

        self.simulation = Simulation(self.traffic_volume, self.rows, self.cols, self.road_length, self.simulation_time)

    def print_statistics(self):
        accumulated_waiting_time = 0
        cars_leaving_simulator = 0

        # Virtual outer intersection
        while not self.simulation.outer_intersection.v_queue.empty():
            accumulated_waiting_time += self.simulation.outer_intersection.v_queue.get().waiting_time
            cars_leaving_simulator += 1
        while not self.simulation.outer_intersection.h_queue.empty():
            accumulated_waiting_time += self.simulation.outer_intersection.h_queue.get().waiting_time
            cars_leaving_simulator += 1

        # Map intersections
        for i, row in enumerate(self.simulation.city_map):
            for j, intersection in enumerate(row):
                while not intersection.v_queue.empty():
                    accumulated_waiting_time += intersection.v_queue.get().waiting_time
                while not intersection.h_queue.empty():
                    accumulated_waiting_time += intersection.h_queue.get().waiting_time

        average_waiting_time = accumulated_waiting_time / cars_leaving_simulator if cars_leaving_simulator > 0 else 'no cars left the simulator'

        print("\n---- STATISTICS ----")
        print("Cars created: " + str(self.simulation.cars_created))
        print("Cars eliminated: " + str(cars_leaving_simulator))
        print("Percentage of cars that have crossed the model: " + str(cars_leaving_simulator / self.simulation.cars_created))
        print("Average waiting time: " + str(average_waiting_time))

    def train(self):
        env = DynamicTrafficControlEnv(self.simulation)

        if exists('models/' + self.model_name + '.zip'):
            model = PPO.load('models/' + self.model_name, env=env)
        else:
            model = PPO(policy='MultiInputPolicy', env=env, verbose=1)

        while True:
            model.learn(total_timesteps=40960, n_eval_episodes=10)
            model.save('models/' + self.model_name)
            _ = env.reset()

    def predict(self):
        env = DynamicTrafficControlEnv(self.simulation)
        model = PPO.load('models/' + self.model_name, env=env)
        observation = env.reset()

        done = False
        while not done:
            action = model.predict(observation)
            observation, rewards, done, info = env.step(action[0])

    def standard(self):
        self.simulation.start_simulation()
        last_time_lights_changed = 0

        done = False
        while not done:
            if (self.simulation.current_time - last_time_lights_changed) >= self.time_between_changes:
                last_time_lights_changed = self.simulation.current_time
                done = self.simulation.advance_step([1] * self.rows * self.cols)
            else:
                done = self.simulation.advance_step([0] * self.rows * self.cols)


if __name__ == '__main__':
    program = Program()

    if program.operation == 1:
        program.train()
    elif program.operation == 2:
        program.predict()
    elif program.operation == 3:
        program.standard()

    program.print_statistics()
