import random


class Car:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.num_of_direction_changes = 0
        self.expected_arrival_position = 0

        self.driver_speed_factor = random.uniform(1, 1.5)
        self.ONE_CAR_LENGTH_TRAVEL_TIME = 0.5 * self.driver_speed_factor
        self.CROSSING_INTERSECTION_TIME = 2 * self.driver_speed_factor

    def calculate_ideal_travel_time_to_next_position(self, empty_gaps):
        time = self.CROSSING_INTERSECTION_TIME
        time += empty_gaps * self.ONE_CAR_LENGTH_TRAVEL_TIME

        return time

    def calculate_acceleration_penalty(self, situation, cars_crossed):
        if situation == 'STARTING':
            acceleration_penalty = (2 - cars_crossed/4 if 0 < cars_crossed < 8 else 0)
        else:
            acceleration_penalty = (4 - cars_crossed/2 if cars_crossed < 8 else 0)

        return acceleration_penalty * self.driver_speed_factor

    def next_direction(self, direction):
        random_number = random.uniform(0, 1)

        if (self.num_of_direction_changes == 0 and random_number > 0.75) or (self.num_of_direction_changes == 1 and random_number > 0.90):
            self.num_of_direction_changes += 1
            return 'VERTICAL' if direction == 'HORIZONTAL' else 'HORIZONTAL'
        else:
            return direction
