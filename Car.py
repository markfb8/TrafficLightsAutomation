import random


class Car:
    def __init__(self, time):
        self.time = time
        self.waiting_time = 0
        self.num_of_direction_changes = 0

    def new_time(self, time):
        self.time = time

    def add_time(self, time):
        self.waiting_time += time

    def next_direction(self, direction):
        random_number = random.uniform(0, 1)

        if (self.num_of_direction_changes == 0 and random_number > 0.75) or (self.num_of_direction_changes == 1 and random_number > 0.90):
            self.num_of_direction_changes += 1
            return 'VERTICAL' if direction == 'HORIZONTAL' else 'HORIZONTAL'
        else:
            return direction
