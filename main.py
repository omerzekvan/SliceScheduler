# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import ast

import pgdb
import copy
import random


# criteria = 0 # Network Service capacity
criteria = 1 # Priority of Network Slice
Re = 2

functionsCatalog = [{"name":'AMF', "cpu": 2, "availability": 0.6},
                    {"name": 'AUSF', "cpu": 2, "availability": 0.8},
                    {"name": 'NEF', "cpu": 8, "availability": 0.7},
                    {"name": 'NRF', "cpu": 2, "availability": 0.6},
                    {"name": 'NSSF', "cpu": 2, "availability": 0.8},
                    {"name": 'PCF', "cpu": 8, "availability": 0.7},
                    {"name":'SMF', "cpu": 2, "availability": 0.6},
                    {"name": 'UDM', "cpu": 2, "availability": 0.8},
                    {"name": 'UDR', "cpu": 2, "availability": 0.8},
                    {"name": 'UPF', "cpu": 8, "availability": 0.7}
                    ]
servicesCatalog = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]]
sliceRequests = [{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 2, "availability": 0.99},
{"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.99}]

def generateSliceRequests():
    try:
        with open("sliceRequests.txt", "w") as file:

            for l in range(0,30):
                print("L: {}".format(l))

                length = random.randint(2,10)
                vnfChain = []
                remainingVNFs = [i for i in range(10)]
                print(remainingVNFs)

                for len in range(0,length):
                    print("len: {}".format(len))
                    whichVNF = random.randint(0,9-len)
                    print("whichVNF: {}".format(whichVNF))

                    indexOfVNF = remainingVNFs.pop(whichVNF)
                    vnfChain.append(indexOfVNF)

                print(vnfChain)
                priority = random.randint(1, 2)

                av = random.randint(90, 99)/100

                # file.write("{\"services\": , \"priority\": {}, \"availability\": {}}".format( str(priority), str(av)))
                #line = "(\"services\": {} , \"priority\": {}, \"availability\": {})\n".format(str(vnfChain), str(priority), str(av))
                print("Priority: {}".format(priority))
                print("Av: {}".format(av))
                #line = f"{'services': {str(vnfChain)} , 'priority': {str(priority)}, 'availability': {float(av)}}\n"
                line = "{\"services\": %s , \"priority\": %d, \"availability\": %.2f}\n" % (str(vnfChain), priority, av)
                #print(f'Only {i:10d} replicas out of {replicasNeeded} are successfully onboarded')
                file.write(line)

    except Exception as e:
        print("Exception: {}".format(e))
    return


originalNodeCapacities = [100, 100, 100, 100, 100, 100]
nodeCapacity = [100, 100, 100, 100, 100, 100]
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
            db.addNodesToFunc(networkFunction.id, networkFunction.nodes)
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
    generateSliceRequests()

    try:
        with open("sliceRequests.txt", "r") as file_in:
            sliceRequests = []
            for line in file_in:
                line = ast.literal_eval(line)
                print(line)
                sliceRequests.append(line)
    except Exception as e:
        print(e)

    sortedSlices = sorted(sliceRequests, key=lambda d: d['priority'])

    numberOfRequests = len(sortedSlices)

    for index, sorted in enumerate(sortedSlices):
        print("Sorted {}: {}".format(index, sorted))
    outputs = []

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
                            #elif r['priority'] == 2 and r['availability'] < t.availability and t.replicas-1 > t.guests:
                            elif r['priority'] == 2 and t.replicas - 1 > t.guests:
                                t.guests += 1
                                foundT = True
                                numberOfGuests += 1

                                # TODO: Arrange availability
                                break

                     #   sortedServices = sort(Services)
                if not foundT:
                    # Assign new t with capacity 5
                    t = Service(functionsList, 2, r['availability'])
                    TServices.append(t)

                    new_service_id = db.insertService(functionsList, r['availability'])

                    for f in functionsList:

                        type = ""
                        cpu = 1

                        for u in functionsCatalog:
                            if u["name"] == functionsCatalog[f]["name"]:
                                # type = u["name"]
                                cpu = u["cpu"]
                                av = u["availability"]
                                break

                        functionId = db.insertFunction(functionsCatalog[f]["name"], cpu, av, [], new_service_id)

                        netFunc = Function(functionId, functionsCatalog[f]["name"], cpu, av)
                        FFunctions.append(netFunc)
                        # Onboard the function considering the requested slice availability and check the result
                        if r['priority'] == 1:
                            onboardingResult = onboard(netFunc, r['availability'])
                        else:
                            onboardingResult = onboard(netFunc, 0)

                        if onboardingResult == 1:
                            sliceFailed = True
                            break

                        t.replicas = netFunc.replicas

                    if sliceFailed:
                        # Remove other functions of the same service
                        db.deleteFunctions(new_service_id)
                        # Remove the service and other services of the same slice if not used
                        db.deleteService(new_service_id)

                        updateNodes()
                        break

            if not sliceFailed:
                db.activateSlice(new_slice_id)
                satisfiedRequests += 1
        outputs.append("Total Number of requests: {} Number of satisfied requests: {} Number of guests: {}".format(
            numberOfRequests, satisfiedRequests, numberOfGuests))
        #print("Total Number of requests: {} Number of satisfied requests: {} Number of guests: {}".format(numberOfRequests, satisfiedRequests, numberOfGuests))

    for o in outputs:
        print(o)