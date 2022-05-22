# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pgdb
import copy


# criteria = 0 # Network Service capacity
criteria = 1 # Pritority of Network Slice
Re = 2

functionsCatalog = [{"name":'AMF', "cpu": 2, "availability": 0.9}, {"name": 'SMF', "cpu": 2, "availability": 0.8}, {"name": 'UPF', "cpu": 8, "availability": 0.9}]
servicesCatalog = [[0, 1], [2]]
sliceRequests = [{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 2, "availability": 0.99},
{"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.99}]

originalNodeCapacities = [50, 50, 16]
nodeCapacity = [50, 50, 16]
N = len(nodeCapacity)

# Failure probability of a physical node
hN = 0.001

# Make nodes with zero load
def resetNodes():
#    for n, o in zip(nodeCapacity, originalNodeCapacities):
#        n = o

#    nodeCapacity = originalNodeCapacities[:]
#    nodeCapacity = copy.deepcopy(originalNodeCapacities)
    for index, value in enumerate(originalNodeCapacities):
        nodeCapacity[index] = value

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
    def __init__(self, type, cpu, availability):
        self.type = type
        self.cpu = cpu
        self.availability = availability
        self.nodes = []
        self.active = False
        self.replicas = 0
        self.guests = 0

    def setReplicas(self, replicas: int):
        self.replicas = replicas

def areListsEqual(list1, list2):
    return set(list1) == set(list2)

def sort(array=[]):
    """Sort the array by using quicksort."""

    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0]
        for x in array:
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            elif x > pivot:
                greater.append(x)
        # Don't forget to return something!
        return sort(less) + equal + sort(greater)  # Just use the + operator to join lists
    # Note that you want equal ^^^^^ not pivot

    # You need to handle the part at the end of the recursion -
    # when you only have one element in your array, just return the array.
    else:
        return array

def computeNumberOfReplicasNeeded(fAv, targetAv):
    avFN = (1 - hN) * fAv
    for n in range(1, 100):
        avF = 1 - ((1 - avFN) ** n)
        if avF >= targetAv:
            numberOfReplicas = n
            break

    return 0 if avF < targetAv else numberOfReplicas

def onboard(networkFunction, targetAv):
    functionAv = networkFunction.availability
    Rcpu = networkFunction.cpu

    replicasNeeded = computeNumberOfReplicasNeeded(functionAv, targetAv)

    if replicasNeeded == 0:
        print("The number of replicas needed is too high")
        return 1
    # Sort N in decreasing Cn order

    i = 0
    for n in range(N):
        if nodeCapacity[n] >= Rcpu: # Requested CPU

            networkFunction.nodes.append(n)
            nodeCapacity[n] -= Rcpu
            i += 1

        if replicasNeeded <= i:
            print(f'{i:10d} replicas onboarded')
            networkFunction.setReplicas(replicasNeeded)
            return 0

    print(f'Only {i:10d} replicas out of {replicasNeeded} are successfully onboarded')
    return 1

def updateNodes():
    resetNodes()
    rows = db.getFunctions()
    for r in rows:
        cpuNeed = r[1]
        nodes = r[5]
        for n in nodes:
            nodeCapacity[n] -= cpuNeed


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    db = pgdb.DBConn()
    db.connect()
    #EFunctions = []

    #Dts = []

    #undoList = []
    #sort(Slices)
    #sortedSlices = dict(sorted(sliceRequests.items(), key=lambda item: item[1]))


    sortedSlices = sorted(sliceRequests, key=lambda d: d['priority'])
    numberOfRequests = len(sortedSlices)

    print(sortedSlices)

    for control in range(0,2):

        TServices = []
        FFunctions = []  # Really needed?
        resetNodes()
        satisfiedRequests = 0
        numberOfGuests = 0

        # Delete all from Functions
        db.deleteFunctions(-1)

        for r in sortedSlices:

            new_slice_id = db.insertSlice(r['services'], r['availability'])

            sliceFailed = False
            for s in r["services"]:

                #success = False
                foundT = False
                functionsList = servicesCatalog[s]

                if control == 1:
                    for t in TServices:
                        tIndex = TServices.index(t)

                        #intSet = t.functions.intersection(functionsSet)

                        # If this is the service we are looking for and has enough capacity use it
                        if set(t.functions) == set(functionsList):
                            if criteria == 0 and t.capacity > 1: #t.functions == len(intSet) and t.capacity > 0:
                                t.capacity -= 1

                                uT = t.capacity
                                foundT = True
                                numberOfGuests += 1
                                # TODO: Arrange availability
                                break
                            elif r['priority'] == 2 and r['availability'] < t.availability and t.replicas-1 > t.guests:
                                t.guests += 1
                                foundT = True
                                numberOfGuests += 1

                                # TODO: Arrange availability
                                break

                     #   sortedServices = sort(Services)
                if foundT == False:
                    # Assign new t with capacity 5
                    t = Service(functionsList, 2, r['availability'])
                    TServices.append(t)

                    new_service_id = db.insertService(functionsList, r['availability'])

                    for f in functionsList:

                        type = ""
                        cpu = 1

                        for u in functionsCatalog:
                            if u["name"] == functionsCatalog[f]["name"]:
                                #type = u["name"]
                                cpu = u["cpu"]
                                av = u["availability"]
                                break

                        netFunc = Function(functionsCatalog[f]["name"], cpu, av)
                        FFunctions.append(netFunc)

                        # TODO: Add availability value
                        db.insertFunction(functionsCatalog[f]["name"], cpu, av, [], new_service_id)
                        # Onboard the function considering the requested slice avilability and check the result
                        if onboard(netFunc, r['availability']) == 1:
                            sliceFailed = True
                            break

                        t.replicas = netFunc.replicas

                    if sliceFailed == True:
                        # Remove other functions of the same service
                        db.deleteFunctions(new_service_id)
                        # Remove the service and other services of the same slice if not used
                        db.deleteService(new_service_id)

                        updateNodes()
                        break

            if sliceFailed == False:
                db.activateSlice(new_slice_id)
                satisfiedRequests += 1

        print("Total Number of requests: {} Number of satisfied requests: {} Number of guests: {}".format(numberOfRequests, satisfiedRequests, numberOfGuests))