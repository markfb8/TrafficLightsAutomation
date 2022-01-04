import Simulation
from Event import Event
from queue import Queue


class Intersection:

    def __init__(self, simulation, max_size_h, max_size_v):
        self.simulation = simulation
        self.green_light = 'VERTICAL'
        self.v_queue = Queue(max_size_v)
        self.h_queue = Queue(max_size_h)
        self.v_out_intersection = None
        self.h_out_intersection = None

    def get_attributes_given_direction(self, direction):
        if direction == 'VERTICAL':
            return self.v_queue, self.v_out_intersection
        else:
            return self.h_queue, self.h_out_intersection

    def switch_traffic_light(self):
        self.green_light = 'VERTICAL' if self.green_light == 'HORIZONTAL' else 'HORIZONTAL'

        queue, _ = self.get_attributes_given_direction(self.green_light)
        if not queue.empty():
            self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + Simulation.CROSSING_AFTER_GREEN, self.green_light, self))

    def move_car(self, event):
        this_queue, out_intersection = self.get_attributes_given_direction(event.direction)
        out_queue, out_out_intersection = out_intersection.get_attributes_given_direction(event.direction)

        # If (green light) and (out queue has space for the car)
        if self.green_light == event.direction and out_queue.qsize() < out_queue.maxsize:
            # If not event created for the out intersection
            if out_queue.empty() and out_out_intersection is not None:
                self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + Simulation.CROSSING_STREET_AND_INTERSECTION, event.direction, out_intersection))

            car = this_queue.get()
            car.add_time(self.simulation.current_time - car.time)
            car.new_time(self.simulation.current_time)
            out_queue.put(car)

            # If there are more cars waiting
            if not this_queue.empty():
                self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + Simulation.CROSSING_BEHIND_CAR, event.direction, self))

        # If (green light) and (out queue does not have space for the car)
        elif self.green_light == event.direction and out_queue.qsize() >= out_queue.maxsize:
            self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + Simulation.CROSSING_AFTER_BUSY_ROAD, event.direction, self))
