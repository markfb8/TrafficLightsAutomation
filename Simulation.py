import MapManager
from Intersection import Intersection

CROSSING_STREET_AND_INTERSECTION = 10
CROSSING_AFTER_GREEN = 5
CROSSING_AFTER_BUSY_ROAD = 3
CROSSING_BEHIND_CAR = 1


class Simulation:
    def __init__(self, traffic_volume: int, rows: int, cols: int, road_length: int, simulation_time: int):
        self.traffic_volume = traffic_volume
        self.rows = rows
        self.cols = cols
        self.road_length = road_length
        self.simulation_time = simulation_time

        self.current_time = 0
        self.event_list = []
        self.outer_intersection = Intersection(self, 99999, 99999)
        self.city_map = None
        self.cars_created = 0

    def add_event(self, event):
        self.event_list.append(event)
        self.event_list.sort(key=lambda x: x.time, reverse=False)

    def start_simulation(self):
        self.city_map = MapManager.create_map(self)
        MapManager.first_cars(self)

    def get_average_waiting_time(self):
        accumulated_waiting_time = 0
        cars_leaving_simulator = 0

        # Virtual outer intersection
        while not self.outer_intersection.v_queue.empty():
            accumulated_waiting_time += self.outer_intersection.v_queue.get().waiting_time
            cars_leaving_simulator += 1
        while not self.outer_intersection.h_queue.empty():
            accumulated_waiting_time += self.outer_intersection.h_queue.get().waiting_time
            cars_leaving_simulator += 1

        # Map intersections
        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                while not intersection.v_queue.empty():
                    accumulated_waiting_time += intersection.v_queue.get().waiting_time
                while not intersection.h_queue.empty():
                    accumulated_waiting_time += intersection.h_queue.get().waiting_time

        # cars_leaving_simulator = self.outer_intersection.v_queue.qsize() + self.outer_intersection.h_queue.qsize()
        average_waiting_time = accumulated_waiting_time / cars_leaving_simulator if cars_leaving_simulator > 0 else 'no cars left the simulator'

        return average_waiting_time, cars_leaving_simulator

    def get_observation(self):
        observation = {
            'lights_settings': [[0] * self.rows * self.cols],
            "horizontal_num_of_cars": [[0] * self.rows * self.cols],
            "vertical_num_of_cars": [[0] * self.rows * self.cols],
            "horizontal_waiting_time": [[-1] * self.road_length] * self.rows * self.cols,
            "vertical_waiting_time": [[-1] * self.road_length] * self.rows * self.cols
            # "average_waiting_time": [self.get_average_waiting_time()[0]]
        }

        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                flattened_index = i * self.cols + j
                observation['lights_settings'][0][flattened_index] = 0 if intersection.green_light == 'VERTICAL' else 1
                observation['horizontal_num_of_cars'][0][flattened_index] = intersection.h_queue.qsize()
                observation['vertical_num_of_cars'][0][flattened_index] = intersection.v_queue.qsize()

                for k, car in enumerate(intersection.h_queue.queue):
                    observation['horizontal_waiting_time'][flattened_index][k] = self.current_time - car.time
                for k, car in enumerate(intersection.v_queue.queue):
                    observation['vertical_waiting_time'][flattened_index][k] = self.current_time - car.time

        return observation

    def change_state(self, action):
        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                if action[i * self.cols + j] >= 0.5:
                    intersection.switch_traffic_light()

    def advance_step(self, action):
        self.change_state(action)

        instant_to_process = self.current_time

        while self.event_list and instant_to_process == self.event_list[0].time:
            if self.current_time <= self.simulation_time:
                current_event = self.event_list.pop(0)
                self.current_time = current_event.time
                if current_event.event_type == 'NEW_CAR':
                    MapManager.new_car(self, current_event)
                else:
                    current_event.intersection.move_car(current_event)
            if self.current_time > self.simulation_time:
                return True

        if self.event_list:
            self.current_time = self.event_list[0].time
        else:
            self.current_time = self.current_time + 1

        return False
