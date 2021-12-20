class Car:
    def __init__(self, time):
        self.time = time
        self.waiting_time = 0

    def newTime(self, time):
        self.time = time

    def addTime(self, time):
        self.waiting_time += time
