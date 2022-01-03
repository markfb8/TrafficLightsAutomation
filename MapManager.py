import numpy as np

from Event import Event
from random import randint

from Intersection import Intersection


def create_map(simulation):
    city_map = np.array([[Intersection(simulation, simulation.road_length, simulation.road_length) for _ in range(simulation.cols)] for _ in range(simulation.rows)])

    for i, row in enumerate(city_map):
        for j, intersection in enumerate(row):
            if i % 2 == 0:  # If in a even row (right connection)
                intersection.connectHOut(city_map[i][j + 1].h_in) if j != simulation.cols - 1 else intersection.connectHOut(simulation.out)
            else:  # If in a odd row (left connection)
                intersection.connectHOut(city_map[i][j - 1].h_in) if j != 0 else intersection.connectHOut(simulation.out)
            if j % 2 == 0:  # If in a even column (down connection)
                intersection.connectVOut(city_map[i + 1][j].v_in) if i != simulation.rows - 1 else intersection.connectVOut(simulation.out)
            else:  # If in a odd column (up connection)
                intersection.connectVOut(city_map[i - 1][j].v_in) if i != 0 else intersection.connectVOut(simulation.out)

    return city_map


def first_cars(simulation):
    for i, row in enumerate(simulation.city_map):
        for j, intersection in enumerate(row):
            if (i % 2 == 0 and j == 0) or (i % 2 != 0 and j == simulation.cols - 1):  # If at the start of an even row or at the end of an odd row, create car
                simulation.addEvent(Event('NEW_CAR', simulation.current_time + calculate_added_time(simulation), 'HORIZONTAL', intersection))
            if (j % 2 == 0 and i == 0) or (j % 2 != 0 and i == simulation.rows - 1):  # If at the start of an even column or at the end of an odd column, create car
                simulation.addEvent(Event('NEW_CAR', simulation.current_time + calculate_added_time(simulation), 'VERTICAL', intersection))


def schedule_next_arrival(simulation, event):
    simulation.cars_created = simulation.cars_created + 1

    simulation.addEvent(Event('NEW_CAR', event.time + calculate_added_time(simulation), event.direction, event.entity))


def calculate_added_time(simulation):
    if simulation.traffic_volume == 1:
        return randint(200, 1000)
    elif simulation.traffic_volume == 2:
        return randint(60, 200)
    elif simulation.traffic_volume == 3:
        return randint(30, 60)
