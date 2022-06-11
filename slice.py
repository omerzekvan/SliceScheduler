class Slice:
  def __init__(self, services, priority, availability):
    self.services = services
    t.priority = priority
    self.availability = availability
    self.active = False

class Service:
    def __init__(self, functions, capacity, availability):
        self.functions = functions
        self.capacity = capacity
        self.availability = availability
        self.active = False
        self.replicas = 0
        self.guests = 0

        def setReplicas(self, replicas: int):
            self.replicas = replicas

class Function:
    def __init__(self, id, type, cpu, availability):
        self.id = id
        self.type = type
        self.cpu = cpu
        self.availability = availability
        self.nodes = []
        self.active = False
        self.replicas = 0
        self.guests = 0

    def setReplicas(self, replicas: int):
        self.replicas = replicas