from Event import Event
from random import randint


class TrainingSource:
    @staticmethod
    def start_simulation(scheduler):
        for i, row in enumerate(scheduler.city_map):
            for j, inter in enumerate(row):
                # Horizontal
                # Street direction: right
                if i % 2 == 0 and j == 0:
                    new_event = Event('NEW_CAR', scheduler.current_time + TrainingSource.calculateAddedTime(scheduler), 'HORIZONTAL', inter)
                # Street direction: left
                elif j == len(scheduler.city_map[0]) - 1:
                    new_event = Event('NEW_CAR', scheduler.current_time + TrainingSource.calculateAddedTime(scheduler), 'HORIZONTAL', inter)
                scheduler.addEvent(new_event)

                # Vertical
                # Street direction: down
                if j % 2 == 0 and i == 0:
                    new_event = Event('NEW_CAR', scheduler.current_time + TrainingSource.calculateAddedTime(scheduler), 'VERTICAL', inter)
                # Street direction: up
                elif len(scheduler.city_map) - 1:
                    new_event = Event('NEW_CAR', scheduler.current_time + TrainingSource.calculateAddedTime(scheduler), 'VERTICAL', inter)
                scheduler.addEvent(new_event)

    @staticmethod
    def scheduleNextArrival(scheduler, event):
        scheduler.cars_created = scheduler.cars_created + 1

        new_event = Event('NEW_CAR', event.time + TrainingSource.calculateAddedTime(scheduler), event.direction, event.entity)
        scheduler.addEvent(new_event)

    @staticmethod
    def calculateAddedTime(scheduler):
        if scheduler.traffic_volume == 1:
            return randint(200, 1000)
        elif scheduler.traffic_volume == 2:
            return randint(60, 200)
        elif scheduler.traffic_volume == 3:
            return randint(30, 60)
