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
        #simstart = Event('SIMULATION_START', 0, None)
        #self.eventList.append(simstart)

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

        # Recollida d'estadístics
        self.recollirEstadistics()

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

    def comprovaCua(self):
        auxqueue = Queue()
        while not self.queue.empty():
            entitat = self.queue.get()
            if (self.currentTime - entitat.created_at) > 15:
                self.clientsperduts = self.clientsperduts + 1
            else:
                auxqueue.put(entitat)

        while not auxqueue.empty():
            self.queue.put(auxqueue.get())

    def recollirEstadistics(self):
        print("")
        print("---- STATISTICS ----")
        print("Customers who payed at checkout 1: " + str(self.server1.entitatstractades))
        print("Customers who payed at checkout 2: " + str(self.server2.entitatstractades))
        print("Customers who payed at checkout 3: " + str(self.server3.entitatstractades))
        print("Customers who payed at checkout 4: " + str(self.server4.entitatstractades))
        avg1 = avg2 = avg3 = avg4 = 0
        if self.server1.entitatstractades != 0:
            avg1 = (self.server1.timeprocessing / self.server1.entitatstractades)
        elif self.server2.entitatstractades != 0:
            avg2 = (self.server2.timeprocessing / self.server2.entitatstractades)
        elif self.server3.entitatstractades != 0:
            avg3 = (self.server3.timeprocessing / self.server3.entitatstractades)
        elif self.server4.entitatstractades != 0:
            avg4 = (self.server4.timeprocessing / self.server4.entitatstractades)
        print("Average process time of supermarket checkouts: " + str((avg1 + avg2 + avg3 + avg4) / 4))
        processed = self.server1.entitatstractades + self.server2.entitatstractades + self.server3.entitatstractades + self.server4.entitatstractades
        print("Average staytime of supermarket queue: " + str(self.staytime / processed))

        if self.clientsperduts == 0:
            print("No lost customers! :)")
        else:
            print("Lost customers: " + str(self.clientsperduts) + " :(")
            print("Lost customers over total number of customers: " + str(
                self.clientsperduts / (avg1 + avg2 + avg3 + avg4 + self.clientsperduts) * 100) + "%")

        print("Checkout 1 was busy: " + str((self.server1.timeprocessing / self.simulationtime) * 100) + "% of simulation time")
        print("Checkout 2 was busy: " + str((self.server2.timeprocessing / self.simulationtime) * 100) + "% of simulation time")
        print("Checkout 3 was busy: " + str((self.server3.timeprocessing / self.simulationtime) * 100) + "% of simulation time")
        print("Checkout 4 was busy: " + str((self.server4.timeprocessing / self.simulationtime) * 100) + "% of simulation time")
        print("")


if __name__ == '__main__':
    scheduler = Scheduler()
    #scheduler.run()
