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

        queue, _ = self.get_attributes_given_direction(self.green_light)
        if not queue.empty():
            # self.simulation.event_list = [event for event in self.simulation.event_list if event.intersection != self or self.green_light != event.direction or event.event_type == 'NEW_CAR']
            # self.simulation.add_event(Event('MOVE_CAR', True, self.simulation.current_time + self.simulation.SWITCH_TO_GREEN_TIME, self.green_light, self))

            event_found = False
            for i, event in enumerate(self.simulation.event_list):
                if event.intersection == self and event.event_type == 'MOVE_CAR' and self.green_light == event.direction:
                    event_found = True
                    break
                    # if self.simulation.current_time < event.time < self.simulation.current_time + self.simulation.SWITCH_TO_GREEN_TIME:
                        # del self.simulation.event_list[i]
                        # self.simulation.add_event(Event('MOVE_CAR', True, self.simulation.current_time + self.simulation.SWITCH_TO_GREEN_TIME, self.green_light, self))

            if not event_found:
                if self.simulation.current_time >= queue.queue[0].arrival_time:
                    from_stop = True
                else:
                    from_stop = False
                event_time = max(queue.queue[0].arrival_time, self.simulation.current_time + self.simulation.SWITCH_TO_GREEN_TIME + 0.1)
                self.simulation.add_event(Event('MOVE_CAR', from_stop, event_time, self.green_light, self))

    def move_car(self, event):
        this_queue, out_intersection = self.get_attributes_given_direction(event.direction)
        out_direction = this_queue.queue[0].next_direction(event.direction)
        out_queue, out_out_intersection = out_intersection.get_attributes_given_direction(out_direction)

        # If (green light) and (light is not changing) and (out queue has space for the car)
        if self.green_light == event.direction and self.simulation.current_time - self.last_light_switch >= self.simulation.SWITCH_TO_GREEN_TIME and out_queue.qsize() < out_queue.maxsize:
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
                if self.simulation.current_time >= this_queue.queue[0].arrival_time:
                    self.simulation.add_event(Event('MOVE_CAR', True, self.simulation.current_time + this_queue.queue[0].ONE_CAR_LENGTH_TRAVEL_TIME, event.direction, self))
                else:
                    time_left_to_arrive = this_queue.queue[0].arrival_time - self.simulation.current_time
                    self.simulation.add_event(Event('MOVE_CAR', False, self.simulation.current_time + time_left_to_arrive + this_queue.queue[0].ONE_CAR_LENGTH_TRAVEL_TIME, event.direction, self))
        # If (green light) and (light is changing)
        elif self.green_light == event.direction and self.simulation.current_time - self.last_light_switch < self.simulation.SWITCH_TO_GREEN_TIME:
            self.simulation.add_event(Event('MOVE_CAR', True, self.last_light_switch + self.simulation.SWITCH_TO_GREEN_TIME + 0.1, event.direction, self))

        # If (green light) and (out queue does not have space for the car)
        elif self.green_light == event.direction and out_queue.qsize() >= out_queue.maxsize:
            self.simulation.add_event(Event('MOVE_CAR', True, self.simulation.current_time + self.simulation.BUSY_ROAD_WAITING_TIME, event.direction, self))
