class Slice:
  def __init__(self, id, services, priority, availability, bw=0, delay=10):
    self.id = id
    self.services = services
    self.priority = priority
    self.availability = availability
    self.bw = bw
    self.delay = delay
    self.active = False
    self.points = 0

class Service:
    def __init__(self, serviceID, reqFunctions, capacity, availability, bw=0, delay=10):
        self.serviceID = serviceID
        self.reqFunctions = reqFunctions
        self.capacity = capacity
        self.availability = availability
        self.bw = bw
        self.delay = delay
        self.active = False
        self.replicas = 0
        #self.guests = 0
        #self.hostedSlices = [] # Link to both the host and guest slices
        self.functions = [] # Link to the network function

    def setReplicas(self, replicas: int):
        self.replicas = replicas

class Function:
    def __init__(self, id, type, cpu, availability, hostServiceId):
        self.id = id
        self.type = type
        self.cpu = cpu
        self.totalCPU = cpu
        self.residualCPU = cpu
        self.availability = availability
        self.hostServiceId = hostServiceId

        self.deployedNodes = []

        self.active = False
        self.guests = 0
        self.pods = []
        self.hostedSlices = [] # Link to both the host and guest slices

    def setReplicas(self, replicas: int):
        self.replicas = replicas

class Pod:
    def __init__(self, type, cpu, node):
        self.type = type
        self.cpu = cpu
        self.residualCPU = cpu
        self.active = False
        self.guests = 0

        self.node = node

class Node:
  def __init__(self, ID, capacity):
    self.ID = ID
    self.capacity = capacity
    self.remCapacity = capacity

  def __repr__(self):
    return f"Node(ID: {self.ID}, Capacity: {self.capacity})"

  @staticmethod
  def sort_by_capacity(nodes):
    """Sorts an array of nodes by their capacity using quicksort.

    Args:
      nodes: A list of Node objects.

    Returns:
      A new list of Node objects sorted by capacity in ascending order.
    """

    if len(nodes) <= 1:
      return nodes

    pivot = nodes[0]
    less = [node for node in nodes if node.capacity < pivot.capacity]
    equal = [node for node in nodes if node.capacity == pivot.capacity]
    greater = [node for node in nodes if node.capacity > pivot.capacity]

    return Node.sort_by_capacity(greater) + equal + Node.sort_by_capacity(less)
  
  @staticmethod
  def sort_by_remCapacity(nodes, reverse = False):
    """Sorts an array of nodes by their remCapacity using quicksort.

    Args:
      nodes: A list of Node objects.

    Returns:
      A new list of Node objects sorted by remCapacity in ascending order.
    """

    if len(nodes) <= 1:
      return nodes

    pivot = nodes[0]
    less = [node for node in nodes if node.remCapacity < pivot.remCapacity]
    equal = [node for node in nodes if node.remCapacity == pivot.remCapacity]
    greater = [node for node in nodes if node.remCapacity > pivot.remCapacity]

    if reverse == False:
      return Node.sort_by_remCapacity(less) + equal + Node.sort_by_remCapacity(greater)
    else:
       return Node.sort_by_remCapacity(greater, True) + equal + Node.sort_by_remCapacity(less, True)
  @staticmethod
  def reset_nodes(nodes):
    """Resets the remCapacity of each Node in the array to its capacity.

    Args:
      nodes: A list of Node objects.
    """

    for node in nodes:
        node.remCapacity = node.capacity

