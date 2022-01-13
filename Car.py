import random


class Car:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.num_of_direction_changes = 0

        driver_speed_factor = random.uniform(1, 1.5)

        self.REACTION_TIME = 1 * driver_speed_factor
        self.ONE_CAR_LENGTH_TRAVEL_TIME = 0.5 * driver_speed_factor
        self.CROSSING_INTERSECTION_TIME = 2 * driver_speed_factor

    def calculate_travel_time_to_next_position(self, from_stop, cross_intersection, empty_gaps):
        time = self.REACTION_TIME if from_stop else 0
        time += self.CROSSING_INTERSECTION_TIME if cross_intersection else 0
        time += empty_gaps * self.ONE_CAR_LENGTH_TRAVEL_TIME

        return time

    def calculate_time_to_next_event(self, from_stop):
        time = self.REACTION_TIME if from_stop else 0
        time += self.ONE_CAR_LENGTH_TRAVEL_TIME

        return time

    def next_direction(self, direction):
        random_number = random.uniform(0, 1)

        if (self.num_of_direction_changes == 0 and random_number > 0.75) or (self.num_of_direction_changes == 1 and random_number > 0.90):
            self.num_of_direction_changes += 1
            return 'VERTICAL' if direction == 'HORIZONTAL' else 'HORIZONTAL'
        else:
            return direction
