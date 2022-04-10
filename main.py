# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pg.py

db = DBConn()
db.connect()

Re = 2

functionsCatalog = [{"name":'AMF', "cpu": 2}, {"name": 'SMF', "cpu": 2}, {"name": 'UPF', "cpu": 8}]
servicesCatalog = [{'AMF', 'SMF'}, {'UPF'}]
sliceRequests = [{"services": [0, 1], "availability": 0.99}]

nodeCapacity = [10, 10, 10, 10, 10]
N = len(nodeCapacity)

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

    replicaCount = computeNumberOfReplicasNeeded(Av)

    # Sort N in decreasing Cn order

    i = 0
    for n in range(N):
        if replicaCount > i  and nodeCapacity[n] >= Rcpu: # Requested CPU

            # xfn = 1
            networkFunction.nodes.append(n)
            nodeCapacity[n] -= Rcpu
            i += 1
        elif replicaCount <= i:
            break
    print(f'{i:10d} replicas onboarded')
    #print(f'{name:10} ==> {phone:10d}')
    if replicaCount <= i:
        return 0
    else:
        return 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    TServices = []
    EFunctions = []
    FFunctions = []

    Dts = []

    undoList = []

    #sort(Slices)

    for r in sliceRequests:

        db.insertSlice(r['services'], r['availability'])

        sliceFailed = False
        for s in r["services"]:

            # Condition already satisfied
            # if Bsl == 1:
            success = False
            foundT = False

            functionsSet = servicesCatalog[s]
            for t in TServices:
                tIndex = TServices.index(t)

                intSet = t.functions.intersection(functionsSet)

                # If this is the service we are looking for and has enough capacity use it
                if t.functions == len(intSet) and t.capacity > 0:
                    t.capacity -= 1

                    uT = t.capacity


                    foundT = True
                    # TODO: Arrange availability
                    break

                 #   sortedServices = sort(Services)
            if foundT == False:
                # Assign new t
                t = Service(functionsSet, 5)
                TServices.append(t)

                new_service_id = db.insertService(functionsSet)

                for f in functionsSet:
                    # TODO new F
                    for u in functionsCatalog:
                        if u["name"] == f:
                            nonlocal type = u["name"]
                            nonlocal cpu = u["cpu"]
                            break

                    netFunc = Function(f, cpu, r["availability"])
                    FFunctions.append(netFunc)

                    db.insertFunction(type, cpu, {}, new_service_id)
                    # Onboard the function and check the result
                    if onboard(netFunc) == 1:
                        sliceFailed = True
                        break

                if sliceFailed == True:
                # TODO: Previous function onboardings of the same slice should be undone
                    break

