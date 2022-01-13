class Event:
    def __init__(self, event_type, from_stop, time, direction, intersection):
        self.event_type = event_type
        self.from_stop = from_stop
        self.time = time
        self.direction = direction
        self.intersection = intersection
