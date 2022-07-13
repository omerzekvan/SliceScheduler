class Slice:
  def __init__(self, services, priority, availability):
    self.services = services
    t.priority = priority
    self.availability = availability
    self.active = False

class Service:
    def __init__(self, reqFunctions, capacity, availability):
        self.reqFunctions = reqFunctions
        self.capacity = capacity
        self.availability = availability
        self.active = False
        self.replicas = 0
        self.guests = 0
        self.fDeployments = []

        def setReplicas(self, replicas: int):
            self.replicas = replicas

class Function:
    def __init__(self, id, type, cpu, availability):
        self.id = id
        self.type = type
        self.cpu = cpu
        self.totalCPU = cpu
        self.residualCPU = cpu
        self.availability = availability
        self.nodes = []
        self.active = False
        self.replicas = 0
        self.guests = 0
        self.pods = []

    def setReplicas(self, replicas: int):
        self.replicas = replicas

class Pod:
    def __init__(self, type, cpu):
        self.type = type
        self.cpu = cpu
        self.residualCPU = cpu
        self.active = False
        self.guests = 0