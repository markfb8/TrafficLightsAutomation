from Event import Event
from random import randint

class Source:
    def __init__(self, scheduler):
        self.trafficvolume = scheduler.trafficvolume
        self.scheduler = scheduler
        self.cityMap = scheduler.cityMap
        self.createdCars = 0


    def processEvent(self, event):
        if event.eventType == 'SIMULATION_START':
            self.simulationStart()
        elif event.eventType == 'NEW_CAR':
            self.scheduleNextArrival(event)


    def simulationStart(self):
        for i,row in enumerate(self.cityMap):
            for j,inter in enumerate(row):
                    # Horizontal
                    # Street direction: right
                    if i % 2 == 0 and j == 0:
                        newEvent = self.nextArrival(self.scheduler.currentTime, 'HORIZONTAL', inter)
                    # Street direction: left
                    elif j == len(self.cityMap[0]) - 1:
                        newEvent = self.nextArrival(self.scheduler.currentTime, 'HORIZONTAL', inter)

                    self.scheduler.addEvent(newEvent)

                    # Vertical
                    # Street direction: down
                    if j % 2 == 0 and i == 0:
                        newEvent = self.nextArrival(self.scheduler.currentTime, 'VERTICAL', inter)
                    # Street direction: up
                    elif len(self.cityMap) - 1:
                        newEvent = self.nextArrival(self.scheduler.currentTime, 'VERTICAL', inter)

                    self.scheduler.addEvent(newEvent)
                    self.scheduler.addEvent(self.startLights(self.scheduler.currentTime, None, inter))




    def nextArrival(self, time, direction, entity):
        addedtime = self.calculateAddedTime()
        return Event('NEW_CAR', time + addedtime, direction, entity)

    def startLights(self, time, direction, entity):
        return Event('SWITCH_TRAFFIC_LIGHT', time, direction, entity)


    def scheduleNextArrival(self, event):
        self.createdCars = self.createdCars + 1
        # Schedule next car creation
        newEvent = self.nextArrival(event.time, event.direction, event.entity)
        self.scheduler.addEvent(newEvent)


    def calculateAddedTime(self):
        if self.trafficvolume == 1:
            return randint(80, 200)
        elif self.trafficvolume == 2:
            return randint(20, 80)
        elif self.trafficvolume == 3:
            return randint(5, 20)
