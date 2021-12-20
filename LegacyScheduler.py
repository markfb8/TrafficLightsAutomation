import math
from queue import Queue
from Source import *
from Event import Event
import numpy as np
from Intersection import *

class Scheduler:
    cars = 0
    current_time = 0
    out = Queue()
    eventList = []

    def __init__(self):
        # Config parameters
        # Volume of arrivals
        print("")
        print("Traffic density: (1, 2 o 3):")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        self.traffic_volume = int(input())
       
        # City map size
        print("")
        print("City map size:")
        print("Rows")
        self.rows = int(input())
        print("Cols")
        self.cols = int(input())

        # Road length
        print("")
        print("Road length (number of cars):")
        self.road_length = int(input())
        
        # Simulation time
        print("Simulation time in minutes:")
        self.simulation_time = int(input()) * 60

        # Print chosen parameters
        print("")
        print("SELECTED PARAMETERS:")
        print("Traffic density: " + str(self.traffic_volume))
        print("Simulation time: " + str(self.simulation_time / 60) + " minutes")

        # Create a map of intersections
        self.createMap()

        # Car generator
        self.source = Source(self)

        # Statistics
        self.stayTime = 0

        # Start simulation 
        self.eventList.append(Event('SIMULATION_START', 0, None, None))

    def createMap(self):
        self.city_map = np.full((self.rows, self.cols), Intersection(self, self.road_length, self.road_length))

        for i,row in enumerate(self.city_map):
            for j,inter in enumerate(row):
                # Horizontal connections
                # Street direction: right
                if i % 2 == 0:
                    if j != self.cols-1:
                        inter.connectHOut(self.city_map[i][j + 1].h_in)
                    else:
                        inter.connectVOut(self.out)

                # Street direction: left
                else:
                    if j != 0:
                        inter.connectHOut(self.city_map[i][j - 1].h_in)
                    else:
                        inter.connectVOut(self.out)

                # Vertical connections
                # Street direction: down
                if j % 2 == 0:
                    if i != self.rows-1:
                        inter.connectVOut(self.city_map[i + 1][j].v_in)
                    else:
                        inter.connectVOut(self.out)
                # Street direction: up
                else:
                    if i != 0:
                        inter.connectVOut(self.city_map[i - 1][j].v_in)
                    else:
                        inter.connectVOut(self.out)

    def run(self):
        # Simulation time at 0
        self.current_time = 0
        # Simulation loop (stops when no events remain at queue or simulation time is over)
        while self.eventList and self.current_time <= self.simulation_time:
            event = self.eventList[0]
            self.eventList.pop(0)
            self.current_time = event.time
            # Event entity processes the event
            if event.entity is None:
                if event.event_type == "SIMULATION_START":
                    self.source.processEvent(event)
            else:
                event.entity.processEvent(event)
                if event.event_type == 'NEW_CAR':

                    self.source.processEvent(event)

        self.statistics()

    def addEvent(self, event):
        self.eventList.append(event)
        self.eventList.sort(key=lambda x: x.time, reverse=False)

    def calcWaitingTime(self):
        time = 0
        i = 0

        while not self.out.empty():
            time += self.out.get().waiting_time
            i += 1

        average_waiting_time = time / i if i > 0 else 'no cars left the simulator'

        return average_waiting_time


    def statistics(self):
        print(" ")
        print("---- STATISTICS ----")
        print("Cars created: " + str(self.source.createdCars))
        print("Cars eliminated: " + str(self.out.qsize()))
        print("Percentage of cars that have travessed the model: " + str(self.out.qsize()/self.source.createdCars))
        print("Average waiting time: " + str(self.calcWaitingTime()))



if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
