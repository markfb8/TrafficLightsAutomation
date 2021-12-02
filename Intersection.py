from Event import Event
from queue import Queue

class Intersection:

    def __init__(self, scheduler, maxSizeH, maxSizeV):
        # init
        self.scheduler = scheduler
        self.VtrafficLight = "GREEN"
        self.HtrafficLight = "RED"
        # roads
        self.maxSizeH = maxSizeH
        self.maxSizeV = maxSizeV
        self.hIn = Queue(maxSizeH)
        self.vIn = Queue(maxSizeV)

    def connectVOut(self, vOut):
        self.vOut = vOut

    def connectHOut(self, hOut):
        self.hOut = hOut
    
    def processEvent(self, event):
        if event.eventType == 'NEW_CAR': # if street is not full a car spawns
            if event.direction == 'VERTICAL':
                if len(self.vIn) + 1 < self.maxSizeV:
                    self.vIn.put(Car(event.time))
            elif event.direction == 'HORIZONTAL':
                if len(self.hIn) + 1 < self.maxSizeH:
                    self.hIn.put(Car(event.time))
        elif event.eventType == 'SWITCH_TRAFFIC_LIGHT':
            self.switchTrafficLight()
        elif event.eventType == 'MOVE_CAR':
            self.moveCar(event.direction)
    
    def switchTrafficLight(self):
        if(self.VtrafficLight == 'RED'):
            self.HtrafficLight == 'RED'
            self.VtrafficLight = 'GREEN'
            scheduleNextCar('VERTICAL')
        elif(self.VtrafficLight == 'GREEN'):
            self.VtrafficLight = 'RED'
            self.HtrafficLight == 'GREEN'
            scheduleNextCar('HORIZONTAL')
        self.scheduler.addEvent(Event('SWITCH_TRAFFIC_LIGHT', self.scheduler.currentTime + 20, None, self))

    def moveCar(direction):
        if direction == 'VERTICAL':
            if len(self.vOut) + 1 < maxSizeV:
                self.vOut.put(self.vIn.get())
        elif direction == 'HORIZONTAL':
            if len(self.hOut) + 1 < maxSizeH:
                self.hOut.put(self.hIn.get())
        self.scheduleNextCar(direction)

    def scheduleNextCar(direction):
        if direction == 'VERTICAL' and self.VtrafficLight == 'GREEN':
            if not self.vIn.isEmpty():
                self.scheduler.addEvent(Event('MOVE_CAR', self.scheduler.currentTime + 2, direction, self))
        if direction == 'HORIZONTAL' and self.HtrafficLight == 'GREEN':
            if not self.hIn.isEmpty():
                self.scheduler.addEvent(Event('MOVE_CAR', self.scheduler.currentTime + 2, direction, self))
        
        

