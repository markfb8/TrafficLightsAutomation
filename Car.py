class Car:
    def __init__(self, time):
        self.time = time
        self.waitingTime = 0

    def newTime(self, time):
        self.time = time

    def addTime(self, time):
        self.waitingTime += time
