from queue import Queue
from Source import *
from Event import Event
import numpy as np
from Intersection import *

class Scheduler:
    currentTime = 0
    eventList = []

    def __init__(self):
        # Config parameters
        
        # Volume of arrivals
        print("")
        print("Traffic density: (1, 2 o 3):")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        self.trafficDensity = int(input())
       
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
        self.roadLength = int(input())
        
        # Simulation time
        print("Simulation time in minutes:")
        self.simulationtime = int(input())

        # Print chosen parameters
        print("")
        print("SELECTED PARAMETERS:")
        print("Traffic density: " + str(self.trafficDensity))
        print("Simulation time: " + str(self.simulationtime) + " minutes")

        # Create a map of intersections
        self.createMap()

        # Statistics

        # Start simulation 
        self.eventList.append(Event('SIMULATION_START', 0, None))

    def createMap(self):
        self.cityMap = np.full((self.rows, self.cols), Intersection(self, self.roadLength, self.roadLength))

        for i,row in enumerate(self.cityMap):
            for j,inter in enumerate(row):
                # Horizontal connections
                # Street direction: right
                if i % 2 == 0:
                    if j != self.cols-1:
                        inter.connectHOut(self.cityMap[i][j+1].hIn)
                        print("Intersection (" + str(i) + "," + str(j) +") connected to (" + str(i) + "," + str(j+1) +")")
                # Street direction: left
                else:
                    if j != 0:
                        inter.connectHOut(self.cityMap[i][j-1].hIn)
                        print("Intersection (" + str(i) + "," + str(j) +") connected to (" + str(i) + "," + str(j-1) +")")

                # Vertical connections
                # Street direction: down
                if j % 2 == 0:
                    if i != self.rows-1:
                        inter.connectHOut(self.cityMap[i+1][j].vIn)
                        print("Intersection (" + str(i) + "," + str(j) +") connected to (" + str(i+1) + "," + str(j) +")")
                # Street direction: up
                else:
                    if i != 0:
                        inter.connectHOut(self.cityMap[i-1][j].vIn)
                        print("Intersection (" + str(i) + "," + str(j) +") connected to (" + str(i-1) + "," + str(j) +")")

    def run(self):
        # Rellotge de simulacio a 0
        self.currentTime = 0
        # Bucle de simulació (condició fi simulació llista buida)
        while self.eventList and self.currentTime <= self.simulationtime:
            # Recuperem event simulacio i el treiem de la llista
            event = self.eventList[0]
            self.eventList.pop(0)
            # Actualitzem el rellotge de simulacio
            self.currentTime = event.time
            # Deleguem l'acció a realitzar de l'esdeveniment a l'objecte que l'ha generat
            # També podríem delegar l'acció a un altre objecte
            if event.entitat is None:
                if event.tipus == "SIMULATION_START":
                    # comunicar a tots els objectes que cal preparar-se
                    self.source.tractarEsdeveniment(event)
                    self.server1.tractarEsdeveniment(event)
                    self.server2.tractarEsdeveniment(event)
                    self.server3.tractarEsdeveniment(event)
                    self.server4.tractarEsdeveniment(event)
            else:
                if event.tipus == 'NEW_SERVICE':
                    if not self.queue.empty():
                        c = self.queue.get()
                        self.staytime = self.staytime + (self.currentTime - c.created_at)
                        event.entitat.recullEntitat(event.time, c)
                else:
                    event.entitat.tractarEsdeveniment(event)
                    if event.tipus == "END_SERVICE":
                        self.comprovaCua()

    def afegirEsdeveniment(self, event):
        # Inserir esdeveniment de forma ordenada
        self.eventList.append(event)
        # Ordenar eventlist per temps
        self.eventList.sort(key=lambda x: x.time, reverse=False)

    def tractarEsdeveniment(self, event):
        if event.tipus == "SIMULATION_START":
            # comunicar a tots els objectes que cal preparar-se
            self.source.tractarEsdeveniment(event)
            self.server1.tractarEsdeveniment(event)
            self.server2.tractarEsdeveniment(event)
            self.server3.tractarEsdeveniment(event)
            self.server4.tractarEsdeveniment(event)

if __name__ == '__main__':
    scheduler = Scheduler()
    #scheduler.run()
