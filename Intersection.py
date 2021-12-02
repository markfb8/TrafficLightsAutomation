from Event import Event
from queue import Queue

class Intersection:

    def __init__(self, scheduler, maxSizeH, maxSizeV):
        # init
        self.Vstate = "idle"
        self.Hstate = "idle"
        self.scheduler = scheduler
        self.VtrafficLight = "GREEN"
        self.HtrafficLight = "RED"
        # roads
        self.maxSizeH = maxSizeH
        self.maxSizeV = maxSizeV
        self.hIn = Queue(maxSizeH)
        self.vIn = Queue(maxSizeV)

    def simulationStart(self):
        self.Vstate = "idle"
        self.Hstate = "idle"

    def connectVOut(self, vOut):
        self.intersectionOutV = vOut

    def connectHOut(self, hOut):
        self.intersectionOutH = hOut
    
    def tractarEsdeveniment(self, event):
        if event.type == 'SIMULATION_START':
            self.simulationStart()
        elif event.type == 'ARRIVAL':
            if event.direction == 'VERTICAL':
                self.processVCarArrival(event.entity)
            elif event.direction == 'HORIZONTAL':
                self.processHCarArrival(event.entity)
        elif event.type == 'SWITCH_TRAFFIC_LIGHT':
            self.switchTrafficLight()
        elif event.type == 'MOVE_CAR':
            moveCar(event.direction)
    
    def processVCarArrival(self, entity):
        if len(self.vOut) + 1 < self.maxSizeV:
            self.vOut.put(entity)
        else: self.Vstate = "busy"

    def processHCarArrival(self, entity):
        if len(self.hOut) + 1 < self.maxSizeH:
            self.hOut.put(entity)
        else: self.Hstate = "busy"
    
    def switchTrafficLight(self):
        if(self.VtrafficLight == 'RED'):
            self.HtrafficLight == 'RED'
            self.VtrafficLight = 'GREEN'
            scheduleNextCar('VERTICAL')
        elif(self.VtrafficLight == 'GREEN'):
            self.VtrafficLight = 'RED'
            self.HtrafficLight == 'GREEN'
            scheduleNextCar('HORIZONTAL')
        self.scheduler.afegirEsdeveniment(Event('SWITCH_TRAFFIC_LIGHT', self.scheduler.currentTime + 20, None, self))

    def moveCar(direction):
        if direction == 'VERTICAL':
            if not self.intersectionOutV.Vstate == "busy":
                self.Vstate = "idle"
                self.intersectionOutV.vIn.put(self.vIn.get())
        elif direction == 'HORIZONTAL':
            if not self.intersectionOutH.Hstate == "busy":
                self.Hstate = "idle"
                self.intersectionOutH.hIn.put(self.hIn.get())
        self.scheduleNextCar(direction)

    def scheduleNextCar(direction):
        if direction == 'VERTICAL' and self.VtrafficLight == 'GREEN':
            if not self.vIn.isEmpty():
                self.scheduler.afegirEsdeveniment(Event('MOVE_CAR', self.scheduler.currentTime + 2, direction, self))
        if direction == 'HORIZONTAL' and self.HtrafficLight == 'GREEN':
            if not self.hIn.isEmpty():
                self.scheduler.afegirEsdeveniment(Event('MOVE_CAR', self.scheduler.currentTime + 2, direction, self))
        
        

