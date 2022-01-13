import MapManager
from Intersection import Intersection


class Simulation:
    def __init__(self, traffic_volume: int, rows: int, cols: int, road_length: int, simulation_time: int):
        self.traffic_volume = traffic_volume
        self.rows = rows
        self.cols = cols
        self.road_length = road_length
        self.simulation_time = simulation_time

        self.SWITCH_TO_GREEN_TIME = 3
        self.BUSY_ROAD_WAITING_TIME = 3

        self.current_time = 0
        self.cars_created = 0
        self.event_list = []
        self.outer_intersection = Intersection(self, 99999, 99999)
        self.city_map = MapManager.create_map(self)
        MapManager.first_cars(self)

    def add_event(self, event):
        self.event_list.append(event)
        self.event_list.sort(key=lambda x: x.time, reverse=False)

    def get_average_waiting_time(self):
        cars_leaving_simulator = self.outer_intersection.v_queue.qsize() + self.outer_intersection.h_queue.qsize()

        accumulated_waiting_time = 0
        # Virtual outer intersection
        for car in list(self.outer_intersection.v_queue.queue):
            accumulated_waiting_time += car.waiting_time
        for car in list(self.outer_intersection.h_queue.queue):
            accumulated_waiting_time += car.waiting_time
        # Map intersections
        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                for car in list(intersection.v_queue.queue):
                    accumulated_waiting_time += car.waiting_time
                for car in list(intersection.h_queue.queue):
                    accumulated_waiting_time += car.waiting_time

        average_waiting_time = accumulated_waiting_time / cars_leaving_simulator if cars_leaving_simulator > 0 else 999999999

        return average_waiting_time, cars_leaving_simulator

    def get_observation(self):
        observation = {
            'lights_settings': [[0] * self.rows * self.cols],
            "horizontal_num_of_cars": [[0] * self.rows * self.cols],
            "vertical_num_of_cars": [[0] * self.rows * self.cols],
            "horizontal_waiting_time": [[-1] * self.road_length] * self.rows * self.cols,
            "vertical_waiting_time": [[-1] * self.road_length] * self.rows * self.cols,
            "average_waiting_time": [[self.get_average_waiting_time()[0]]]
        }

        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                flattened_index = i * self.cols + j
                observation['lights_settings'][0][flattened_index] = 0 if intersection.green_light == 'VERTICAL' else 1
                observation['horizontal_num_of_cars'][0][flattened_index] = intersection.h_queue.qsize()
                observation['vertical_num_of_cars'][0][flattened_index] = intersection.v_queue.qsize()

                for k, car in enumerate(intersection.h_queue.queue):
                    observation['horizontal_waiting_time'][flattened_index][k] = self.current_time - car.arrival_time
                for k, car in enumerate(intersection.v_queue.queue):
                    observation['vertical_waiting_time'][flattened_index][k] = self.current_time - car.arrival_time

        return observation

    def change_state(self, action):
        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                if action[i * self.cols + j] >= 0.5:
                    intersection.switch_traffic_light()

    def advance_step(self, action, single_processing_mode=True):
        self.change_state(action)

        instant_to_process = self.current_time

        while self.event_list and self.event_list[0].time - instant_to_process <= 10:
            if self.current_time <= self.simulation_time:
                current_event = self.event_list.pop(0)
                self.current_time = current_event.time
                if current_event.event_type == 'NEW_CAR':
                    MapManager.new_car(self, current_event)
                else:
                    current_event.intersection.move_car(current_event)
            else:
                return True
            if single_processing_mode:
                break

        if self.event_list:
            self.current_time = self.event_list[0].time
        else:
            self.current_time = self.current_time + 1

        return False
