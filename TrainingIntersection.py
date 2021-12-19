from Car import Car
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
                if self.vIn.qsize() + 1 < self.maxSizeV:
                    self.vIn.put(Car(event.time))
            elif event.direction == 'HORIZONTAL':
                if self.hIn.qsize() + 1 < self.maxSizeH:
                    self.hIn.put(Car(event.time))
        elif event.eventType == 'SWITCH_TRAFFIC_LIGHT':
            self.switchTrafficLight()
        elif event.eventType == 'MOVE_CAR':
            self.moveCar(event.direction)
    
    def switchTrafficLight(self):
        self.VtrafficLight = 'GREEN' if self.VtrafficLight == 'RED' else 'RED'
        self.HtrafficLight = 'GREEN' if self.HtrafficLight == 'RED' else 'RED'

        if self.VtrafficLight == 'GREEN':
            self.scheduler.addEvent(Event('MOVE_CAR', self.scheduler.current_time + 2, "VERTICAL", self))
        else:
            self.scheduler.addEvent(Event('MOVE_CAR', self.scheduler.current_time + 2, "HORIZONTAL", self))

    def moveCar(self, direction):
        if direction == 'VERTICAL':
            if (not self.vIn.empty()) and self.VtrafficLight == 'GREEN' and (self.vOut.maxsize == 0 or self.vOut.qsize() + 1 < self.vOut.maxsize):
                car = self.vIn.get()
                car.addTime(self.scheduler.current_time - car.time)
                car.newTime(self.scheduler.current_time)
                self.vOut.put(car)
        elif direction == 'HORIZONTAL':
            if (not self.vIn.empty()) and self.HtrafficLight == 'GREEN' and (self.vOut.maxsize == 0 or self.hOut.qsize() + 1 < self.hOut.maxsize):
                car = self.hIn.get()
                car.addTime(self.scheduler.current_time - car.time)
                car.newTime(self.scheduler.current_time)
                self.hOut.put(car)
        self.scheduler.addEvent(Event('MOVE_CAR', self.scheduler.current_time + 2, direction, self))
