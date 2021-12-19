from Source import *
import numpy as np
from Intersection import *


class Scheduler:
    def __init__(self, traffic_volume: int, rows: int, cols: int, road_length: int, simulation_time: int):
        self.traffic_volume = traffic_volume
        self.rows = rows
        self.cols = cols
        self.road_length = road_length
        self.simulation_time = simulation_time
        self.current_time = 0
        self.event_list = []
        self.out = Queue()
        self.city_map = None

        self.createMap()

        self.source = Source(self)

    def createMap(self):
        self.city_map = np.full((self.rows, self.cols), Intersection(self, self.road_length, self.road_length))

        for i, row in enumerate(self.city_map):
            for j, inter in enumerate(row):
                # Horizontal connections
                # Street direction: right
                if i % 2 == 0:
                    if j != self.cols - 1:
                        inter.connectHOut(self.city_map[i][j + 1].hIn)
                    else:
                        inter.connectVOut(self.out)

                # Street direction: left
                else:
                    if j != 0:
                        inter.connectHOut(self.city_map[i][j - 1].hIn)
                    else:
                        inter.connectVOut(self.out)

                # Vertical connections
                # Street direction: down
                if j % 2 == 0:
                    if i != self.rows - 1:
                        inter.connectVOut(self.city_map[i + 1][j].vIn)
                    else:
                        inter.connectVOut(self.out)
                # Street direction: up
                else:
                    if i != 0:
                        inter.connectVOut(self.city_map[i - 1][j].vIn)
                    else:
                        inter.connectVOut(self.out)

    def addEvent(self, event):
        self.event_list.append(event)
        self.event_list.sort(key=lambda x: x.time, reverse=False)

    def statistics(self):
        def calcWaitingTime():
            time = 0
            i = 0

            while not self.out.empty():
                time += self.out.get().waitingTime
                i += 1

            average_waiting_time = time / i if i > 0 else 'no cars left the simulator'

            return average_waiting_time

        print("\n---- STATISTICS ----")
        print("Cars created: " + str(self.source.createdCars))
        print("Cars eliminated: " + str(self.out.qsize()))
        print("Percentage of cars that have travessed the model: " + str(self.out.qsize() / self.source.createdCars))
        print("Average waiting time: " + str(calcWaitingTime()))

    def start_simulation(self):
        self.event_list.append(Event('SIMULATION_START', 0, None, None))
        current_event = self.event_list.pop(0)
        self.current_time = current_event.time
        self.source.processEvent(current_event)

    def get_observation(self):
        observation = {
            'lights_settings': [0] * self.rows * self.cols,
            "horizontal_num_of_cars": [0] * self.rows * self.cols,
            "vertical_num_of_cars": [0] * self.rows * self.cols,
            "horizontal_waiting_time": [[0] * self.road_length] * self.rows * self.cols,
            "vertical_waiting_time": [[0] * self.road_length] * self.rows * self.cols
        }

        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                flattened_index = i*self.cols+j
                observation['lights_settings'][flattened_index] = 1 if intersection.HtrafficLight == "GREEN" else 0
                observation['horizontal_num_of_cars'][flattened_index] = intersection.hIn.qsize()
                observation['vertical_num_of_cars'][flattened_index] = intersection.vIn.qsize()

                for k, car in enumerate(intersection.hIn):
                    observation['horizontal_waiting_time'][flattened_index][k] = car.waitingTime
                for k, car in enumerate(intersection.vIn):
                    observation['vertical_waiting_time'][flattened_index][k] = car.waitingTime

        return observation

    def change_state(self, action):
        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                if action(i * self.cols + j) == 1:
                    intersection.switchTrafficLight()

    def advance_step(self, action):
        self.change_state(action)

        done = not self.event_list or self.current_time > self.simulation_time

        if not done:
            current_event = self.event_list.pop(0)
            self.current_time = current_event.time

            current_event.entity.processEvent(current_event)
            if current_event.eventType == 'NEW_CAR':
                self.source.processEvent(current_event)
        else:
            self.statistics()

        return done
