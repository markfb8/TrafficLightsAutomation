import random
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
        self.last_density_change = 0
        self.vertical_density = 0.5
        self.is_vertical_density_increasing = random.choice([True, False])
        self.intersection_to_process = 0
        self.event_list = []
        self.outer_intersection = Intersection(self, 99999, 99999)
        self.city_map = MapManager.create_map(self)
        MapManager.manage_simulation_entry_points(self)

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
                    accumulated_waiting_time += car.waiting_time + self.current_time - car.arrival_time
                for car in list(intersection.h_queue.queue):
                    accumulated_waiting_time += car.waiting_time + self.current_time - car.arrival_time

        average_waiting_time = accumulated_waiting_time / self.cars_created if self.cars_created != 0 else 999999

        return average_waiting_time, cars_leaving_simulator

    def get_observation(self):
        i = int(self.intersection_to_process / self.cols)
        j = self.intersection_to_process % self.cols
        intersection = self.city_map[i][j]
        v_in = intersection.v_in_intersection
        h_in = intersection.h_in_intersection
        v_out = intersection.v_out_intersection
        h_out = intersection.h_out_intersection

        observation = dict()
        observation['lights_settings'] = [int(intersection.green_light == 'HORIZONTAL')]
        observation['intersection_cars'] = [intersection.v_queue.qsize(), intersection.h_queue.qsize()]
        # observation['input_cars'] = [0 if intersection.v_in_intersection is None else v_in.v_queue.qsize(), 0 if intersection.h_in_intersection is None else h_in.h_queue.qsize()]
        observation['output_cars'] = [-1 if v_out.v_out_intersection is None else v_out.v_queue.qsize(), -1 if h_out.h_out_intersection is None else h_out.h_queue.qsize()]

        return observation

    def change_traffic_density(self):
        if self.current_time - self.last_density_change > 600:
            if self.is_vertical_density_increasing:
                if self.vertical_density < 0.8:
                    self.vertical_density += 0.1
                else:
                    self.is_vertical_density_increasing = False
            else:
                if self.vertical_density > 0.2:
                    self.vertical_density -= 0.1
                else:
                    self.is_vertical_density_increasing = True

    def change_all_lights(self):
        for row in self.city_map:
            for intersection in row:
                intersection.switch_traffic_light()

    def change_state(self, action):
        # 0 = Not change light, 1 = Change light
        if action == 1:
            i = int(self.intersection_to_process / self.cols)
            j = self.intersection_to_process % self.cols

            self.city_map[i][j].switch_traffic_light()

        if self.intersection_to_process < self.rows * self.cols - 1:
            self.intersection_to_process += 1
        else:
            self.intersection_to_process = 0

    def advance_step(self, action):
        # self.change_state(action)
        self.change_state(action)

        self.change_traffic_density()

        if self.current_time <= self.simulation_time:
            if self.event_list:
                current_event = self.event_list.pop(0)
                self.current_time = current_event.time
                if current_event.event_type == 'NEW_CAR':
                    MapManager.new_car(self, current_event)
                else:
                    current_event.intersection.move_car(current_event)
            else:
                self.current_time = self.current_time + 1
        else:
            return True

        return False
