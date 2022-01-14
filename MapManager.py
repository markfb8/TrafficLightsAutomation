from queue import Queue

import numpy as np

from Car import Car
from Event import Event
from random import randint

from Intersection import Intersection
import Simulation


def create_map(simulation):
    city_map = np.array([[Intersection(simulation, simulation.road_length, simulation.road_length) for _ in range(simulation.cols)] for _ in range(simulation.rows)])

    for i, row in enumerate(city_map):
        for j, intersection in enumerate(row):
            if i % 2 == 0:  # If in a even row (right connection)
                intersection.h_out_intersection = city_map[i][j + 1] if j != simulation.cols - 1 else simulation.outer_intersection
            else:  # If in a odd row (left connection)
                intersection.h_out_intersection = city_map[i][j - 1] if j != 0 else simulation.outer_intersection
            if j % 2 == 0:  # If in a even column (down connection)
                intersection.v_out_intersection = city_map[i + 1][j] if i != simulation.rows - 1 else simulation.outer_intersection
            else:  # If in a odd column (up connection)
                intersection.v_out_intersection = city_map[i - 1][j] if i != 0 else simulation.outer_intersection

    return city_map


def manage_simulation_entry_points(simulation):
    for i, row in enumerate(simulation.city_map):
        for j, intersection in enumerate(row):
            if (i % 2 == 0 and j == 0) or (i % 2 != 0 and j == simulation.cols - 1):  # If at the start of an even row or at the end of an odd row
                intersection.h_queue = Queue(1000)
                simulation.add_event(Event('NEW_CAR', None, 0, 'HORIZONTAL', intersection))
            if (j % 2 == 0 and i == 0) or (j % 2 != 0 and i == simulation.rows - 1):  # If at the start of an even column or at the end of an odd column
                intersection.v_queue = Queue(1000)
                simulation.add_event(Event('NEW_CAR', None, 0, 'VERTICAL', intersection))


def new_car(simulation, event):
    queue, _ = event.intersection.get_attributes_given_direction(event.direction)

    if queue.qsize() < queue.maxsize:
        simulation.cars_created = simulation.cars_created + 1
        car = Car(simulation.current_time)
        travel_time_to_next_position = car.calculate_travel_time_to_next_position(False, False, simulation.road_length - queue.qsize())
        car.arrival_time = simulation.current_time + travel_time_to_next_position
        queue.put(car)
        simulation.add_event(Event('NEW_CAR', None, event.time + calculate_added_time(simulation), event.direction, event.intersection))
        if queue.qsize() == 1:
            simulation.add_event(Event('MOVE_CAR', False, simulation.current_time + travel_time_to_next_position, event.direction, event.intersection))
    else:
        simulation.add_event(Event('NEW_CAR', None, event.time + 2, event.direction, event.intersection))


def calculate_added_time(simulation):
    if simulation.traffic_volume == 1:
        return randint(60, 120)
    elif simulation.traffic_volume == 2:
        return randint(30, 60)
    elif simulation.traffic_volume == 3:
        return randint(15, 30)
    elif simulation.traffic_volume == 4:
        return randint(6, 15)
    elif simulation.traffic_volume == 5:
        return randint(3, 6)
    elif simulation.traffic_volume == 6:
        return randint(1, 3)
