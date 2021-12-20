from Event import Event
from random import randint


class Source:
    def __init__(self, scheduler):
        self.traffic_volume = scheduler.traffic_volume
        self.scheduler = scheduler
        self.city_map = scheduler.city_map
        self.createdCars = 0

    def processEvent(self, event):
        if event.event_type == 'SIMULATION_START':
            self.simulationStart()
        elif event.event_type == 'NEW_CAR':
            self.scheduleNextArrival(event)

    def simulationStart(self):
        for i, row in enumerate(self.city_map):
            for j, inter in enumerate(row):
                # Horizontal
                # Street direction: right
                if i % 2 == 0 and j == 0:
                    new_event = self.nextArrival(self.scheduler.current_time, 'HORIZONTAL', inter)
                # Street direction: left
                elif j == len(self.city_map[0]) - 1:
                    new_event = self.nextArrival(self.scheduler.current_time, 'HORIZONTAL', inter)

                self.scheduler.addEvent(new_event)

                # Vertical
                # Street direction: down
                if j % 2 == 0 and i == 0:
                    new_event = self.nextArrival(self.scheduler.current_time, 'VERTICAL', inter)
                # Street direction: up
                elif len(self.city_map) - 1:
                    new_event = self.nextArrival(self.scheduler.current_time, 'VERTICAL', inter)

                self.scheduler.addEvent(new_event)
                self.scheduler.addEvent(self.startLights(self.scheduler.current_time, None, inter))

    def nextArrival(self, time, direction, entity):
        added_time = self.calculateAddedTime()
        return Event('NEW_CAR', time + added_time, direction, entity)

    def startLights(self, time, direction, entity):
        return Event('SWITCH_TRAFFIC_LIGHT', time, direction, entity)

    def scheduleNextArrival(self, event):
        self.createdCars = self.createdCars + 1
        # Schedule next car creation
        new_event = self.nextArrival(event.time, event.direction, event.entity)
        self.scheduler.addEvent(new_event)

    def calculateAddedTime(self):
        if self.traffic_volume == 1:
            return randint(200, 1000)
        elif self.traffic_volume == 2:
            return randint(60, 200)
        elif self.traffic_volume == 3:
            return randint(30, 60)
