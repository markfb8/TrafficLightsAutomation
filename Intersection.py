import Simulation
from Event import Event
from queue import Queue


class Intersection:
    def __init__(self, simulation, max_size_h, max_size_v):
        self.simulation = simulation
        self.green_light = 'VERTICAL'
        self.last_light_switch = 0
        self.cars_crossed = 0
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
        self.cars_crossed = 0

        queue, _ = self.get_attributes_given_direction(self.green_light)
        if not queue.empty():
            event = next(iter([i for i in self.simulation.event_list if i.intersection == self and i.event_type == 'MOVE_CAR' and self.green_light == i.direction]), None)

            # if not event_found:
            if event is None:
                event_time = max(queue.queue[0].arrival_time, self.simulation.current_time + self.simulation.SWITCH_TO_GREEN_TIME)
                self.simulation.add_event(Event('MOVE_CAR', event_time, self.green_light, self))

    def move_car(self, event):
        this_queue, out_intersection = self.get_attributes_given_direction(event.direction)
        out_direction = this_queue.queue[0].next_direction(event.direction)
        out_queue, out_out_intersection = out_intersection.get_attributes_given_direction(out_direction)

        # If (green light) and (light is not changing) and (out queue has space for the car)
        if self.green_light == event.direction and (self.simulation.current_time+0.1) - self.last_light_switch >= self.simulation.SWITCH_TO_GREEN_TIME and out_queue.qsize() < out_queue.maxsize:
            car = this_queue.get()
            ideal_travel_time_to_next_position = car.calculate_ideal_travel_time_to_next_position(self.simulation.road_length - out_queue.qsize())
            acceleration_penalty = car.calculate_acceleration_penalty('CROSSING', self.cars_crossed) if self.simulation.current_time > car.arrival_time else 0
            car.waiting_time += self.simulation.current_time - car.arrival_time
            car.arrival_time = self.simulation.current_time + ideal_travel_time_to_next_position + acceleration_penalty
            car.expected_arrival_position = out_queue.qsize()
            out_queue.put(car)

            # If not event created for the out intersection
            if out_queue.qsize() == 1 and out_out_intersection is not None:
                self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + ideal_travel_time_to_next_position + acceleration_penalty, out_direction, out_intersection))

            # If there are more cars waiting
            if not this_queue.empty():
                next_car = this_queue.queue[0]
                if self.simulation.current_time > next_car.arrival_time:
                    time_until_next_event = next_car.ONE_CAR_LENGTH_TRAVEL_TIME + car.calculate_acceleration_penalty('STARTING', self.cars_crossed)
                else:
                    time_until_next_event = (next_car.arrival_time - self.simulation.current_time) + next_car.expected_arrival_position * next_car.ONE_CAR_LENGTH_TRAVEL_TIME
                    next_car.arrival_time = self.simulation.current_time + time_until_next_event

                self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + time_until_next_event, event.direction, self))

            self.cars_crossed += 1
        # If (green light) and (light is changing)
        elif self.green_light == event.direction and self.simulation.current_time - self.last_light_switch < self.simulation.SWITCH_TO_GREEN_TIME:
            self.simulation.add_event(Event('MOVE_CAR', self.last_light_switch + self.simulation.SWITCH_TO_GREEN_TIME, event.direction, self))

        # If (green light) and (out queue does not have space for the car)
        elif self.green_light == event.direction and out_queue.qsize() >= out_queue.maxsize:
            self.simulation.add_event(Event('MOVE_CAR', self.simulation.current_time + self.simulation.BUSY_ROAD_WAITING_TIME, event.direction, self))
