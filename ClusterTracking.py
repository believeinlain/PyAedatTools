
class Cluster:
    def __init__(self, x, y, events):
        self.x = x
        self.y = y
        self.events = events

class ClusterTracker:
    def __init__(self):
        self.clusters = []
        self.eventBuffer = []
        self.oldestEvent

    def 