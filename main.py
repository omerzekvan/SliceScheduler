# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import ast
import pgdb
import slice
import copy
import random
import time

# criteria = 0 # Network Service capacity
criteria = 1 # Priority of Network Slice
Re = 2

functionsCatalog = [{"name":'AMF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'AUSF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'NEF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'NRF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'NSSF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'PCF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name":'SMF', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'UDM', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'UDR', "cpu": 2, "availability": 0.9, "reqCount": 0},
                    {"name": 'UPF', "cpu": 8, "availability": 0.9, "reqCount": 0}
                    ]
servicesCatalog = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]]
sliceRequests = [{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 2, "availability": 0.99},
{"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.99}]

oneNodeCPU = 100
originalNodeCapacities = sorted([oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True)
nodeCapacity = sorted([oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True)
N = len(nodeCapacity)

# Failure probability of a physical node
hN = 0.001

def generateSliceRequests(numberOfRequests : int):
    try:
        with open("sliceRequests.txt", "w") as file:

            for l in range(0,numberOfRequests):
                print("L: {}".format(l))

                # Number of NFs in a network slice
                length = random.randint(6,10)
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

                av = random.randint(80, 99)/100

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

def countCNFRequests(sliceRequests=[]):


    for l in sliceRequests:
        for s in l["services"]:
            functionsCatalog[s]["reqCount"] += 1

def rateSlices():
    for l in sliceRequests:
        #prior = 10 if l["priority"] == 1 else 2
        #l["points"] = 10**6 * prior
        l["points"] = 10 ** 6 * l["priority"]
        for s in l["services"]:
            l["points"] += functionsCatalog[s]["reqCount"] + 10**3 * functionsCatalog[s]["cpu"]

# Make nodes with zero load
def resetNodes():
    for index, value in enumerate(originalNodeCapacities):
        nodeCapacity[index] = value

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

# Onboarding a function means there is not other shared function that can be used
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
        # Current capacity is enough, so onboard the NF
        if nodeCapacity[n] >= Rcpu:

            networkFunction.nodes.append(n)
            nodeCapacity[n] -= Rcpu
            i += 1

            networkFunction.pods.append(slice.Pod(networkFunction.type, networkFunction.cpu))

        if replicasNeeded <= i:
            print(f'{i:10d} replicas onboarded')
            networkFunction.setReplicas(replicasNeeded)
            db.addNodesToFunc(networkFunction.id, networkFunction.nodes)

            networkFunction.totalCPU = networkFunction.cpu * i
            networkFunction.residualCPU = networkFunction.cpu * (i - 1)
            return 0

    networkFunction.totalCPU = networkFunction.cpu * i
    networkFunction.residualCPU = networkFunction.cpu * (i-1)

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

    maxNumberOfReqs = 100
    numberOfExperiments = 1

    try:
        db = pgdb.DBConn()
        db.connect()
    except Exception as e:
        print(e)

    for numberOfReqs in range(10, maxNumberOfReqs+1 , 10):
        outputs = []
        sumOfSharedUtil = 0
        sumOfNonSharedUtil = 0
        sumOfNonSSatisfiedReqs = 0
        sumOfSSatisfiedReqs = 0
        sumOfGuestFunctions = 0
        sumOfGuestSlices = 0
        sumOfProposedUtil = 0
        sumOfPSatisfiedReqs = 0
        sumOfPGuestFunctions = 0
        sumOfPGuestSlices = 0

        noShareTotalTime = 0
        TSMTotalTime = 0
        CNFSHTotalTime = 0



        for experiment in range(0,numberOfExperiments):
            #undoList = []
            #sort(Slices)
            #sortedSlices = dict(sorted(sliceRequests.items(), key=lambda item: item[1]))
            generateSliceRequests(numberOfReqs)

            with open("sliceRequests.txt", "r") as file_in:
                sliceRequests = []
                for line in file_in:
                    line = ast.literal_eval(line)
                    print(line)
                    sliceRequests.append(line)

            numberOfRequests = len(sliceRequests)



            for control in range(0,3):

                TServices = []
                FFunctions = []  # Really needed?
                resetNodes()
                satisfiedRequests = 0
                numberOfGuestFunctions = 0
                numberOfGuestSlices = 0

                # Delete all from Functions
                db.deleteFunctions(-1)

                #Start Time
                startTime = time.time()

                if control == 2:
                    countCNFRequests(sliceRequests)
                    rateSlices()
                    sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                elif control == 1:
                    sortedSlices = sorted(sliceRequests, key=lambda d: d['priority'])
                else:
                    # For the first two models there is no sorting
                    sortedSlices = sliceRequests

                for index, sortedSlice in enumerate(sortedSlices):
                    print("Sorted {}: {}".format(index, sortedSlice))

                for r in sortedSlices:

                    new_slice_id = db.insertSlice(r['services'], r['availability'])

                    isGuest = False
                    sliceFailed = False
                    for s in r["services"]:

                        #success = False
                        foundT = False
                        functionsList = servicesCatalog[s]

                        if control > 0:
                            for t in TServices:
                                tIndex = TServices.index(t)

                                #intSet = t.functions.intersection(functionsSet)

                                # If this is the service we are looking for and has enough capacity use it
                                if set(t.reqFunctions) == set(functionsList):
                                    if criteria == 0 and t.capacity > 1: #t.reqFunctions == len(intSet) and t.capacity > 0:
                                        t.capacity -= 1

                                        foundT = True
                                        numberOfGuestFunctions += 1
                                        isGuest = True
                                        # TODO: Arrange availability
                                        break
                                    #elif r['priority'] == 2 and r['availability'] < t.availability and t.replicas-1 > t.guests:
                                    #elif r['priority'] == 2 and t.replicas - 1 > t.guests:
                                    elif r['priority'] == 2 and t.fDeployments[0].residualCPU >= functionsCatalog[functionsList[0]]["cpu"]:
                                        t.guests += 1
                                        foundT = True
                                        numberOfGuestFunctions += 1
                                        isGuest = True
                                        t.fDeployments[0].residualCPU -= functionsCatalog[functionsList[0]]["cpu"]

                                        # TODO: Arrange availability
                                        break

                             #   sortedServices = sort(Services)
                        if not foundT:
                            # Assign new t with capacity 5
                            t = slice.Service(functionsList, 2, r['availability'])
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

                                netFunc = slice.Function(functionId, functionsCatalog[f]["name"], cpu, av)
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
                                t.fDeployments.append(netFunc)

                            if sliceFailed:
                                # Remove other functions of the same service
                                db.deleteFunctions(new_service_id)
                                # Remove the service and other services of the same slice if not used
                                db.deleteService(new_service_id)
                                TServices.pop()

                                updateNodes()
                                break

                    if not sliceFailed:
                        db.activateSlice(new_slice_id)
                        satisfiedRequests += 1
                        if isGuest: numberOfGuestSlices += 1

                #End time
                endTime = time.time()

                # Calculations for Utilization
                totalUtilization = 0

                duration = endTime - startTime

                for index, c in enumerate(nodeCapacity):
                    totalUtilization += originalNodeCapacities[index] - c

                #Average utilization per satisfied slice request
                avrgUtil = totalUtilization / satisfiedRequests
                if control == 0:
                    sumOfNonSharedUtil += avrgUtil
                    sumOfNonSSatisfiedReqs += satisfiedRequests
                    noShareTotalTime += duration
                elif control == 1:
                    sumOfSharedUtil += avrgUtil
                    sumOfSSatisfiedReqs += satisfiedRequests
                    sumOfGuestFunctions += numberOfGuestFunctions
                    sumOfGuestSlices += numberOfGuestSlices
                    TSMTotalTime += duration
                else:
                    sumOfProposedUtil+=avrgUtil
                    sumOfPSatisfiedReqs += satisfiedRequests
                    sumOfPGuestFunctions += numberOfGuestFunctions
                    sumOfPGuestSlices += numberOfGuestSlices
                    CNFSHTotalTime += duration

                outputs.append("Total Number of requests: {} Number of satisfied requests: {} Number of guests: {} Average Utilization: {}".format(
                    numberOfRequests, satisfiedRequests, numberOfGuestSlices, avrgUtil))
                #print("Total Number of requests: {} Number of satisfied requests: {} Number of guests: {}".format(numberOfRequests, satisfiedRequests, numberOfGuests))

        with open("results.txt", "a") as file1, open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open("guests.txt", "a") as file4, open("timeLine.txt", "a") as file5:
            avrgNonSharedUtil = round(sumOfNonSharedUtil / numberOfExperiments, 2)
            avrgSharedUtil = round(sumOfSharedUtil / numberOfExperiments, 2)
            avrgProposedUtil = round(sumOfProposedUtil / numberOfExperiments, 2)

            avrgNonSSatisfiedReqs = round(sumOfNonSSatisfiedReqs / numberOfExperiments, 0)
            avrgSSatisfiedReqs = round(sumOfSSatisfiedReqs / numberOfExperiments, 0)
            avrgPSatisfiedReqs = round(sumOfPSatisfiedReqs / numberOfExperiments, 0)

            avrgGuests = round(sumOfGuestSlices / numberOfExperiments, 0)
            avrgPGuests = round(sumOfPGuestSlices / numberOfExperiments, 0)

            avrgNoShareTime = round(noShareTotalTime / numberOfExperiments / numberOfReqs, 4)
            avrgTSMTime = round(TSMTotalTime / numberOfExperiments / numberOfReqs, 4)
            avrgCNFSHTime = round(CNFSHTotalTime / numberOfExperiments / numberOfReqs, 4)


            usage = str(avrgNonSharedUtil) + " " + str(avrgSharedUtil) + " " + str(avrgProposedUtil) + "\n"
            satisfied = str(avrgNonSSatisfiedReqs) + " " + str(avrgSSatisfiedReqs) + " " + str(avrgPSatisfiedReqs) + "\n"
            guests =  str(avrgGuests)  + " " + str(avrgPGuests) + "\n"
            timeLine = str(avrgNoShareTime) + " " + str(avrgTSMTime) + " " + str(avrgCNFSHTime) + "\n"

            file2.write(usage)
            file3.write(satisfied)
            file4.write(guests)
            file5.write(timeLine)




            for o in outputs:
                print(o)
                # Writing data to a file
                file1.write(o + "\n")
                #file1.writelines(L)

    with open("results.txt", "a") as file1, open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open(
            "guests.txt", "a") as file4, open("timeLine.txt", "a") as file5:

        file1.write("\n")
        file2.write("\n")
        file3.write("\n")
        file4.write("\n")
        file5.write("\n")
