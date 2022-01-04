class Car:
    def __init__(self, time):
        self.time = time
        self.waiting_time = 0

    def new_time(self, time):
        self.time = time

    def add_time(self, time):
        self.waiting_time += time
