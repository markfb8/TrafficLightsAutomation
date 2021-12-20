import numpy as np

from Event import Event
from random import randint

from Intersection import Intersection


def create_map(scheduler):
    city_map = np.array([[Intersection(scheduler, scheduler.road_length, scheduler.road_length) for _ in range(scheduler.cols)] for _ in range(scheduler.rows)])

    for i, row in enumerate(city_map):
        for j, inter in enumerate(row):
            # Horizontal connections (right)
            if i % 2 == 0:
                if j != scheduler.cols - 1:
                    inter.connectHOut(city_map[i][j + 1].h_in)
                else:
                    inter.connectHOut(scheduler.out)

            # Horizontal connections (left)
            else:
                if j != 0:
                    inter.connectHOut(city_map[i][j - 1].h_in)
                else:
                    inter.connectHOut(scheduler.out)

            # Vertical connections (down)
            if j % 2 == 0:
                if i != scheduler.rows - 1:
                    inter.connectVOut(city_map[i + 1][j].v_in)
                else:
                    inter.connectVOut(scheduler.out)
            # Vertical connections (up)
            else:
                if i != 0:
                    inter.connectVOut(city_map[i - 1][j].v_in)
                else:
                    inter.connectVOut(scheduler.out)

    return city_map


def first_cars(scheduler):
    for i, row in enumerate(scheduler.city_map):
        for j, intersection in enumerate(row):
            # Horizontal (right)
            if i % 2 == 0 and j == 0:
                new_event = Event('NEW_CAR', scheduler.current_time + calculate_added_time(scheduler), 'HORIZONTAL', intersection)
            # Horizontal (left)
            elif j == len(scheduler.city_map[0]) - 1:
                new_event = Event('NEW_CAR', scheduler.current_time + calculate_added_time(scheduler), 'HORIZONTAL', intersection)
            scheduler.addEvent(new_event)

            # Vertical (down)
            if j % 2 == 0 and i == 0:
                new_event = Event('NEW_CAR', scheduler.current_time + calculate_added_time(scheduler), 'VERTICAL', intersection)
            # Vertical (up)
            elif len(scheduler.city_map) - 1:
                new_event = Event('NEW_CAR', scheduler.current_time + calculate_added_time(scheduler), 'VERTICAL', intersection)
            scheduler.addEvent(new_event)


def schedule_next_arrival(scheduler, event):
    scheduler.cars_created = scheduler.cars_created + 1

    new_event = Event('NEW_CAR', event.time + calculate_added_time(scheduler), event.direction, event.entity)
    scheduler.addEvent(new_event)


def calculate_added_time(scheduler):
    if scheduler.traffic_volume == 1:
        return randint(200, 1000)
    elif scheduler.traffic_volume == 2:
        return randint(60, 200)
    elif scheduler.traffic_volume == 3:
        return randint(30, 60)
