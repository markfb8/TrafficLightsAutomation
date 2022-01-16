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
                if j != simulation.cols - 1:
                    city_map[i][j + 1].h_in_intersection = intersection
            else:  # If in a odd row (left connection)
                intersection.h_out_intersection = city_map[i][j - 1] if j != 0 else simulation.outer_intersection
                if j != 0:
                    city_map[i][j - 1].h_in_intersection = intersection
            if j % 2 == 0:  # If in a even column (down connection)
                intersection.v_out_intersection = city_map[i + 1][j] if i != simulation.rows - 1 else simulation.outer_intersection
                if i != simulation.rows - 1:
                    city_map[i + 1][j].v_in_intersection = intersection
            else:  # If in a odd column (up connection)
                intersection.v_out_intersection = city_map[i - 1][j] if i != 0 else simulation.outer_intersection
                if i != 0:
                    city_map[i - 1][j].v_in_intersection = intersection

    return city_map


def manage_simulation_entry_points(simulation):
    for i, row in enumerate(simulation.city_map):
        for j, intersection in enumerate(row):
            if (i % 2 == 0 and j == 0) or (i % 2 != 0 and j == simulation.cols - 1):  # If at the start of an even row or at the end of an odd row
                intersection.h_queue = Queue(1000)
                simulation.add_event(Event('NEW_CAR', 0, 'HORIZONTAL', intersection))
            if (j % 2 == 0 and i == 0) or (j % 2 != 0 and i == simulation.rows - 1):  # If at the start of an even column or at the end of an odd column
                intersection.v_queue = Queue(1000)
                simulation.add_event(Event('NEW_CAR', 0, 'VERTICAL', intersection))


def new_car(simulation, event):
    queue, _ = event.intersection.get_attributes_given_direction(event.direction)

    if queue.qsize() < 1000:
        simulation.cars_created = simulation.cars_created + 1
        car = Car(simulation.current_time)
        car.arrival_time = simulation.current_time + (simulation.road_length - queue.qsize()) * car.ONE_CAR_LENGTH_TRAVEL_TIME
        car.expected_arrival_position = queue.qsize()
        queue.put(car)
        if queue.qsize() == 1:
            simulation.add_event(Event('MOVE_CAR', simulation.current_time + (simulation.road_length - queue.qsize()) * car.ONE_CAR_LENGTH_TRAVEL_TIME, event.direction, event.intersection))

    simulation.add_event(Event('NEW_CAR', event.time + calculate_added_time(simulation, event.direction), event.direction, event.intersection))


def calculate_added_time(simulation, direction):
    time = 0

    if simulation.traffic_volume == 1:
        time = randint(30, 60)
    elif simulation.traffic_volume == 2:
        time = randint(15, 30)
    elif simulation.traffic_volume == 3:
        time = randint(6, 15)
    elif simulation.traffic_volume == 4:
        time = randint(3, 6)

    if direction == 'VERTICAL':
        return time * simulation.vertical_density * 2
    else:
        return time * (1 - simulation.vertical_density) * 2
