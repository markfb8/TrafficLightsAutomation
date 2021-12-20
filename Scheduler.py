from queue import Queue
import MapManager


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
        self.cars_created = 0

    def addEvent(self, event):
        self.event_list.append(event)
        self.event_list.sort(key=lambda x: x.time, reverse=False)

    def print_statistics(self):
        def calc_waiting_time():
            accumulated_waiting_time = 0
            cars_leaving_simulator = 0

            while not self.out.empty():
                accumulated_waiting_time += self.out.get().waiting_time
                cars_leaving_simulator += 1

            average_waiting_time = accumulated_waiting_time / cars_leaving_simulator if cars_leaving_simulator > 0 else 'no cars left the simulator'

            return average_waiting_time

        print("\n---- STATISTICS ----")
        print("Cars created: " + str(self.cars_created))
        print("Cars eliminated: " + str(self.out.qsize()))
        print("Percentage of cars that have crossed the model: " + str(self.out.qsize() / self.cars_created))
        print("Average waiting time: " + str(calc_waiting_time()))

    def start_simulation(self):
        self.city_map = MapManager.create_map(self)
        MapManager.first_cars(self)

    def get_observation(self):
        observation = {
            'lights_settings': [[0] * self.rows * self.cols],
            "horizontal_num_of_cars": [[0] * self.rows * self.cols],
            "vertical_num_of_cars": [[0] * self.rows * self.cols],
            "horizontal_waiting_time": [[-1] * self.road_length] * self.rows * self.cols,
            "vertical_waiting_time": [[-1] * self.road_length] * self.rows * self.cols
        }

        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                flattened_index = i * self.cols + j
                observation['lights_settings'][0][flattened_index] = 1 if intersection.h_traffic_light == "GREEN" else 0
                observation['horizontal_num_of_cars'][0][flattened_index] = intersection.h_in.qsize()
                observation['vertical_num_of_cars'][0][flattened_index] = intersection.v_in.qsize()

                for k, car in enumerate(intersection.h_in.queue):
                    observation['horizontal_waiting_time'][flattened_index][k] = car.waiting_time
                for k, car in enumerate(intersection.v_in.queue):
                    observation['vertical_waiting_time'][flattened_index][k] = car.waiting_time

        return observation

    def change_state(self, action):
        for i, row in enumerate(self.city_map):
            for j, intersection in enumerate(row):
                if action[i * self.cols + j] >= 0.5:
                    intersection.switchTrafficLight()

    def advance_step(self, action):
        self.change_state(action)

        for _ in range(100):
            if self.event_list and self.current_time <= self.simulation_time:
                current_event = self.event_list.pop(0)
                self.current_time = current_event.time
                current_event.entity.processEvent(current_event)
            else:
                return True

        return False
