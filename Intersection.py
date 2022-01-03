from Car import Car
from Event import Event
from queue import Queue
import MapManager


class Intersection:

    def __init__(self, simulation, max_size_h, max_size_v):
        # init
        self.simulation = simulation
        self.v_traffic_light = "GREEN"
        self.h_traffic_light = "RED"
        # roads
        self.max_size_h = max_size_h
        self.max_size_v = max_size_v
        self.h_in = Queue(max_size_h)
        self.v_in = Queue(max_size_v)
        self.v_out = None
        self.h_out = None

    def connectVOut(self, v_out):
        self.v_out = v_out

    def connectHOut(self, h_out):
        self.h_out = h_out

    def processEvent(self, event):
        if event.event_type == 'NEW_CAR':
            MapManager.schedule_next_arrival(self.simulation, event)
            if event.direction == 'VERTICAL':
                if self.v_in.qsize() + 1 < self.max_size_v:
                    self.v_in.put(Car(event.time))
            elif event.direction == 'HORIZONTAL':
                if self.h_in.qsize() + 1 < self.max_size_h:
                    self.h_in.put(Car(event.time))
        elif event.event_type == 'MOVE_CAR':
            self.moveCar(event)

    def switchTrafficLight(self):
        self.v_traffic_light = 'GREEN' if self.v_traffic_light == 'RED' else 'RED'
        self.h_traffic_light = 'GREEN' if self.h_traffic_light == 'RED' else 'RED'

        if self.v_traffic_light == 'GREEN':
            self.simulation.addEvent(Event('MOVE_CAR', self.simulation.current_time + 5, "VERTICAL", self))
        else:
            self.simulation.addEvent(Event('MOVE_CAR', self.simulation.current_time + 5, "HORIZONTAL", self))

    def moveCar(self, event):
        if event.direction == 'VERTICAL':
            if (self.v_traffic_light == 'GREEN' and not self.v_in.empty()) and (self.v_out.maxsize == 0 or self.v_out.qsize() + 1 < self.v_out.maxsize):
                car = self.v_in.get()
                car.addTime(self.simulation.current_time - car.time)
                car.newTime(self.simulation.current_time)
                self.v_out.put(car)
                self.simulation.addEvent(Event('MOVE_CAR', self.simulation.current_time + 1, event.direction, self))
            elif self.v_out.maxsize == 0 or self.v_out.qsize() + 1 < self.v_out.maxsize:
                self.simulation.addEvent(Event('MOVE_CAR', self.simulation.current_time + 2, "VERTICAL", self))

        elif event.direction == 'HORIZONTAL':
            if (self.h_traffic_light == 'GREEN' and not self.h_in.empty()) and (self.h_out.maxsize == 0 or self.h_out.qsize() + 1 < self.h_out.maxsize):
                car = self.h_in.get()
                car.addTime(self.simulation.current_time - car.time)
                car.newTime(self.simulation.current_time)
                self.h_out.put(car)
                self.simulation.addEvent(Event('MOVE_CAR', self.simulation.current_time + 1, event.direction, self))
            elif self.h_out.maxsize == 0 or self.h_out.qsize() + 1 < self.h_out.maxsize:
                self.simulation.addEvent(Event('MOVE_CAR', self.simulation.current_time + 2, 'HORIZONTAL', self))
