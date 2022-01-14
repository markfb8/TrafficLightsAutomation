import Simulation
from Event import Event
from queue import Queue


class Intersection:
    def __init__(self, simulation, max_size_h, max_size_v):
        self.simulation = simulation
        self.green_light = 'VERTICAL'
        self.last_light_switch = 0
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
        self.last_light_switch = self.simulation.current_time

        self.simulation.event_list = [event for event in self.simulation.event_list if event.intersection != self or event.event_type == 'NEW_CAR']

        queue, _ = self.get_attributes_given_direction(self.green_light)
        if not queue.empty():
            self.simulation.add_event(Event('MOVE_CAR', True, self.simulation.current_time + self.simulation.SWITCH_TO_GREEN_TIME, self.green_light, self))

    def move_car(self, event):
        this_queue, out_intersection = self.get_attributes_given_direction(event.direction)
        out_direction = this_queue.queue[0].next_direction(event.direction)
        out_queue, out_out_intersection = out_intersection.get_attributes_given_direction(out_direction)

        # If (green light) and (out queue has space for the car)
        if self.green_light == event.direction and out_queue.qsize() < out_queue.maxsize:
            car = this_queue.get()
            travel_time_to_next_position = car.calculate_travel_time_to_next_position(event.from_stop, True, self.simulation.road_length - out_queue.qsize())
            car.waiting_time += self.simulation.current_time - car.arrival_time
            car.arrival_time = self.simulation.current_time + travel_time_to_next_position
            out_queue.put(car)

            # If not event created for the out intersection
            if out_queue.qsize() == 1 and out_out_intersection is not None:
                self.simulation.add_event(Event('MOVE_CAR', False, self.simulation.current_time + travel_time_to_next_position, out_direction, out_intersection))

            # If there are more cars waiting
            if not this_queue.empty():
                time_to_next_event = this_queue.queue[0].calculate_time_to_next_event(event.from_stop)
                self.simulation.add_event(Event('MOVE_CAR', False, self.simulation.current_time + time_to_next_event, event.direction, self))

        # If (green light) and (out queue does not have space for the car)
        elif self.green_light == event.direction and out_queue.qsize() >= out_queue.maxsize:
            self.simulation.add_event(Event('MOVE_CAR', True, self.simulation.current_time + self.simulation.BUSY_ROAD_WAITING_TIME, event.direction, self))
