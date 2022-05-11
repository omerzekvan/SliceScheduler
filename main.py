# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pgdb



Re = 2

functionsCatalog = [{"name":'AMF', "cpu": 2}, {"name": 'SMF', "cpu": 2}, {"name": 'UPF', "cpu": 8}]
servicesCatalog = [[0, 1], [2]]
sliceRequests = [{"services": [0, 1], "availability": 0.99},
                 {"services": [0, 1], "availability": 0.99},
{"services": [0, 1], "availability": 0.99},
{"services": [0, 1], "availability": 0.99},
{"services": [0, 1], "availability": 0.99},
                 {"services": [0, 1], "availability": 0.99}]

originalNodeCapacities = [10, 10, 16]
nodeCapacity = [10, 10, 16]
N = len(nodeCapacity)

def resetNodes():
    for n, o in zip(nodeCapacity, originalNodeCapacities):
        n = o

class Slice:
  def __init__(self, services, availability):
    self.services = services
    self.availability = availability
    self.active = False

class Service:
    def __init__(self, functions, capacity):
        self.functions = functions
        self.capacity = capacity
        self.active = False

class Function:
    def __init__(self, type, cpu, availability):
        self.type = type
        self.cpu = cpu
        self.availability = availability
        self.nodes = []
        self.active = False

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

def computeNumberOfReplicasNeeded(Av):
    return 1

def onboard(networkFunction):
    Av = networkFunction.availability
    Rcpu = networkFunction.cpu

    replicasNeeded = computeNumberOfReplicasNeeded(Av)

    # Sort N in decreasing Cn order

    i = 0
    for n in range(N):
        if nodeCapacity[n] >= Rcpu: # Requested CPU

            networkFunction.nodes.append(n)
            nodeCapacity[n] -= Rcpu
            i += 1

        if replicasNeeded <= i:
            print(f'{i:10d} replicas onboarded')
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

    TServices = []
    #EFunctions = []
    FFunctions = [] # Really needed?

    #Dts = []

    #undoList = []
    #sort(Slices)

    # Delete all from Functions
    db.deleteFunctions(-1)

    for r in sliceRequests:

        new_slice_id = db.insertSlice(r['services'], r['availability'])

        sliceFailed = False
        for s in r["services"]:

            #success = False
            foundT = False

            functionsList = servicesCatalog[s]
            for t in TServices:
                tIndex = TServices.index(t)

                #intSet = t.functions.intersection(functionsSet)

                # If this is the service we are looking for and has enough capacity use it
                if set(t.functions) == set(functionsList) and t.capacity > 1: #t.functions == len(intSet) and t.capacity > 0:
                    t.capacity -= 1

                    uT = t.capacity

                    foundT = True
                    # TODO: Arrange availability
                    break

                 #   sortedServices = sort(Services)
            if foundT == False:
                # Assign new t with capacity 5
                t = Service(functionsList, 2)
                TServices.append(t)

                new_service_id = db.insertService(functionsList)

                for f in functionsList:

                    type = ""
                    cpu = 1

                    for u in functionsCatalog:
                        if u["name"] == functionsCatalog[f]["name"]:
                            #type = u["name"]
                            cpu = u["cpu"]
                            break

                    netFunc = Function(functionsCatalog[f]["name"], cpu, r["availability"])
                    FFunctions.append(netFunc)

                    # TODO: Add availability value
                    db.insertFunction(functionsCatalog[f]["name"], cpu, [], new_service_id)
                    # Onboard the function and check the result
                    if onboard(netFunc) == 1:
                        sliceFailed = True
                        break

                if sliceFailed == True:
                    # Remove other functions of the same service
                    db.deleteFunctions(new_service_id)
                    # Remove the service and other services of the same slice if not used
                    db.deleteService(new_service_id)

                    updateNodes()
                    break

        if sliceFailed == False:
            db.activateSlice(new_slice_id)
