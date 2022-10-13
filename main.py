# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import ast
import pgdb
import slice
import copy
import random
import time
import numpy as np

from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(np.float64, addapt_numpy_float64)
register_adapter(np.int64, addapt_numpy_int64)

# criteria = 0 # Network Service capacity
criteria = 1 # Priority of Network Slice
Re = 2
NFavailability = 99.9 # In fact np.float128(0.999)

functionsCatalog = [{"name":'AMF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'AUSF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'NEF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'NRF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'NSSF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'PCF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name":'SMF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'UDM', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'UDR', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"name": 'UPF', "cpu": 8, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0}
                    ]
servicesCatalog = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]]
sliceRequests = [{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 2, "availability": 0.99},
{"services": [0, 1], "priority": 2, "availability": 0.9},
{"services": [0, 1], "priority": 1, "availability": 0.99},
                 {"services": [0, 1], "priority": 2, "availability": 0.99}]

oneNodeCPU = 100
originalNodeCapacities = sorted([oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True) #, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True)
nodeCapacity = sorted([oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True) #, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True)
N = len(nodeCapacity)

# Failure probability of a physical node
hN = 0.001
HighAv = 99.99

def generateSliceRequests(numberOfRequests : int):
    try:
        with open("sliceRequests.txt", "w") as file:

            for l in range(0,numberOfRequests):
                print("L: {}".format(l))

                # Number of NFs in a network slice
                length = random.randint(3,10)
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

                #av = random.randint(80, 99)/100

                #In fact av = np.float128(99.999/100) if priority == 1 else 0.9
                av = HighAv if priority == 1 else 90

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
            if l["priority"] == 1:
                functionsCatalog[s]["reqCount"] += 1
            else:
                functionsCatalog[s]["lowReqCount"] += 1


def rateSlices(ratinglevel):
    if ratinglevel == 0:
        for l in sliceRequests:
            #prior = 10 if l["priority"] == 1 else 2
            #l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10**3 * functionsCatalog[s]["cpu"]
    elif ratinglevel == 1:
        for l in sliceRequests:
            size = len(l["services"])
            #prior = 10 if l["priority"] == 1 else 2
            #l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] -= (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 2:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 3:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10 ** 3 * functionsCatalog[s]["cpu"] + (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 4:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10 ** 3 * functionsCatalog[s]["cpu"] - (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 5:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l["priority"] == 1:
                    l["points"] -= (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
                else:
                #if l["priority"] == 2:
                    l["points"] += (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 6:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l["priority"] == 1:
                    l["points"] += (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
                else:
                #if l["priority"] == 2:
                    l["points"] -= (functionsCatalog[s]["reqCount"]  + functionsCatalog[s]["lowReqCount"]) / size
    elif ratinglevel == 7:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l["priority"] == 1:
                    l["points"] -= functionsCatalog[s]["lowReqCount"] / size
                else:
                    # if l["priority"] == 2:
                    l["points"] -= functionsCatalog[s]["reqCount"] / size
    elif ratinglevel == 8:
        for l in sliceRequests:
            size = len(l["services"])
            # prior = 10 if l["priority"] == 1 else 2
            # l["points"] = 10**6 * prior
            l["points"] = 10 ** 6 * l["priority"]
            for s in l["services"]:
                l["points"] += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l["priority"] == 1:
                    l["points"] += functionsCatalog[s]["lowReqCount"] / size
                else:
                    # if l["priority"] == 2:
                    l["points"] += functionsCatalog[s]["reqCount"] / size


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

    # These lines could not be executed due to an issue regarding floating numbers, instead precalulcation is used
    #avFN = np.float128((1 - hN) * fAv)
    #for n in range(1, 100):
    #    avF = 1 - ((1 - avFN) ** n)
    #    if avF >= targetAv:
    #        numberOfReplicas = n
    #        break

    #return 0 if avF < targetAv else numberOfReplicas

    return 2 if targetAv == 99.99 else 1
    #return 3 if targetAv == 99.99 else 1
    #return 2 if targetAv > 0.9 else 1

# Onboarding a function means there is not other shared function that can be used
def onboard(networkFunction, targetAv):
    functionAv = networkFunction.availability
    Rcpu = networkFunction.cpu

    replicasNeeded = computeNumberOfReplicasNeeded(functionAv, targetAv)

    if replicasNeeded == 0:
        print("The number of replicas needed is too high")
        return 0
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
            return i

    networkFunction.totalCPU = networkFunction.cpu * i
    networkFunction.residualCPU = networkFunction.cpu * (i-1)

    print(f'Only {i:10d} replicas out of {replicasNeeded} are successfully onboarded')
    return 0

def updateNodes():
    resetNodes()
    rows = db.getFunctions()
    for r in rows:
        cpuNeed = r[1]
        nodes = r[5]
        for n in nodes:
            nodeCapacity[n] -= cpuNeed

def totalRemainingCapacity():
    total = 0
    for nc in nodeCapacity:
        total += nc

    return total

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    maxNumberOfReqs = 600
    numberOfExperiments = 100

    try:
        db = pgdb.DBConn()
        db.connect()

        with open("results.txt", "a") as file1, open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open(
                    "guests.txt", "a") as file4, open("timeLine.txt", "a") as file5, open("scores.txt", "a") as file6:

            file1.write("NFavailability = {}. 2 pods are onboard if HA({}) is required else only 1 pod is onboard\n".format(NFavailability, HighAv))
            file2.write("NFavailability = {}. 2 pods are onboard if HA({}) is required else only 1 pod is onboard\n".format(NFavailability, HighAv))
            file3.write("NFavailability = {}. 2 pods are onboard if HA({}) is required else only 1 pod is onboard\n".format(NFavailability, HighAv))
            file4.write("NFavailability = {}. 2 pods are onboard if HA({}) is required else only 1 pod is onboard\n".format(NFavailability, HighAv))
            file5.write("NFavailability = {}. 2 pods are onboard if HA({}) is required else only 1 pod is onboard\n".format(NFavailability, HighAv))
            file6.write("NFavailability = {}. 2 pods are onboard if HA({}) is required else only 1 pod is onboard\n".format(NFavailability, HighAv))

        controlGroups = 12
        for numberOfReqs in range(480, maxNumberOfReqs+1 , 30):
            outputs = []

            sumOfUsage = [0]*controlGroups

            sumOfSatisfiedReqs = [0]*controlGroups

            sumOfGuestF = [0]*controlGroups

            sumOfGuestS = [0]*controlGroups

            totalTime = [0]*controlGroups

            scores = [0]*controlGroups

            avrgUsage = [0]*controlGroups
            avrgSatisfiedReqs = [0]*controlGroups
            avrgGuestF = [0]*controlGroups
            avrgGuestS = [0]*controlGroups
            avrgTime = [0]*controlGroups

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

                #numberOfRequests = len(sliceRequests)

                maxSatisfiedRequestsInExperiment = 0

                maxSatisfiedRequestsInExperimentAmongFavs = 0
                bestResultAvrgUtilAmongFavs = 0
                bestResultNumberOfGuestFunctionsAmongFavs = 0
                bestResultNumberOfGuestSlicesAmongFavs = 0
                bestResultDurationAmongFavs = 0

                #List of best performers in the experiment
                winners = []

                # 11 control sets are simulated. The 12th model choses the best among 3 favorite models
                for control in range(0,controlGroups-1):

                    TServices = []
                    FFunctions = []  # Really needed?
                    resetNodes()
                    satisfiedRequests = 0
                    numberOfGuestFunctions = 0
                    numberOfGuestSlices = 0

                    # Delete all from Functions
                    db.deleteFunctions(-1)

                    totalUnderutilized = 0

                    #Start Time
                    startTime = time.time()
                    if control == 10:
                        countCNFRequests(sliceRequests)
                        rateSlices(8)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 9:
                        countCNFRequests(sliceRequests)
                        rateSlices(7)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 8:
                        countCNFRequests(sliceRequests)
                        rateSlices(6)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 7:
                        countCNFRequests(sliceRequests)
                        rateSlices(5)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 6:
                        countCNFRequests(sliceRequests)
                        rateSlices(4)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 5:
                        countCNFRequests(sliceRequests)
                        rateSlices(3)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 4:
                        countCNFRequests(sliceRequests)
                        rateSlices(2)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 3:
                        countCNFRequests(sliceRequests)
                        rateSlices(1)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 2:
                        #countCNFRequests(sliceRequests)
                        rateSlices(0)
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['points'])
                    elif control == 1:
                        sortedSlices = sorted(sliceRequests, key=lambda d: d['priority'])
                    else:
                        # For the first two models there is no sorting
                        sortedSlices = sliceRequests

                    for index, sortedSlice in enumerate(sortedSlices):
                        print("Sorted {}: {}".format(index, sortedSlice))

                    for r in sortedSlices:

                        #if totalRemainingCapacity() < 6 and (r['priority'] == 1 or (r['priority'] == 2 and totalUnderutilized < 6)):
                        #    break
                        if totalRemainingCapacity() < 6 and totalUnderutilized < 6:
                            break

                        new_slice_id = db.insertSlice(r['services'], r['availability'])

                        isGuest = False
                        sliceFailed = False
                        sliceUnderutilized = 0

                        for s in r["services"]:

                            #success = False
                            foundT = False
                            functionsList = servicesCatalog[s]

                            if control > 0 and r['priority'] == 2:
                                for t in TServices:
                                    # tIndex = TServices.index(t)

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
                                        #elif r['priority'] == 2 and t.fDeployments[0].residualCPU >= functionsCatalog[functionsList[0]]["cpu"]:
                                        elif t.fDeployments[0].residualCPU >= functionsCatalog[functionsList[0]]["cpu"]:
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

                                    netFunc = slice.Function(functionId, functionsCatalog[f]["name"], cpu, round(av,6))
                                    FFunctions.append(netFunc)
                                    # Onboard the function considering the requested slice availability and check the result
                                    if r['priority'] == 1:
                                        onboardingResult = onboard(netFunc, r['availability'])
                                    else:
                                        onboardingResult = onboard(netFunc, 0)

                                    if onboardingResult == 0:
                                        sliceFailed = True
                                        break
                                    else: sliceUnderutilized += (onboardingResult-1)*cpu

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
                            totalUnderutilized += sliceUnderutilized

                    #End time
                    endTime = time.time()

                    # Calculations for Utilization
                    totalUtilization = 0

                    duration = endTime - startTime

                    for index, c in enumerate(nodeCapacity):
                        totalUtilization += originalNodeCapacities[index] - c

                    #Average utilization per satisfied slice request
                    avrgUtil = totalUtilization / satisfiedRequests

                    sumOfUsage[control] += avrgUtil
                    sumOfSatisfiedReqs[control] += satisfiedRequests
                    sumOfGuestF[control] += numberOfGuestFunctions
                    sumOfGuestS[control] += numberOfGuestSlices
                    totalTime[control] += duration

                    #If this is the best result so far
                    if maxSatisfiedRequestsInExperiment <  satisfiedRequests:
                        winners = [] # Initialize the winners list, we have a new winner candidate
                        winners.append(control)
                        maxSatisfiedRequestsInExperiment = satisfiedRequests
                    elif maxSatisfiedRequestsInExperiment == satisfiedRequests:
                        winners.append(control)

                    #If this is the best result so far among the chosen models
                    if control == 2 or control == 9 or control == 10:
                        #Calculating the total duration for 3 chosen models
                        bestResultDurationAmongFavs += duration

                        if maxSatisfiedRequestsInExperimentAmongFavs < satisfiedRequests:
                            bestResultAvrgUtilAmongFavs = avrgUtil
                            maxSatisfiedRequestsInExperimentAmongFavs = satisfiedRequests
                            bestResultNumberOfGuestFunctionsAmongFavs = numberOfGuestFunctions
                            bestResultNumberOfGuestSlicesAmongFavs = numberOfGuestSlices

                    outputs.append("Control Set: {} Total Number of requests: {} Number of satisfied requests: {} Number of guests: {} Average Utilization: {}".format(
                        control, numberOfReqs, satisfiedRequests, numberOfGuestSlices, avrgUtil))
                    #print("Total Number of requests: {} Number of satisfied requests: {} Number of guests: {}".format(numberOfReqs, satisfiedRequests, numberOfGuests))

                sumOfUsage[controlGroups-1] += bestResultAvrgUtilAmongFavs
                sumOfSatisfiedReqs[controlGroups-1] += maxSatisfiedRequestsInExperimentAmongFavs
                sumOfGuestF[controlGroups-1] += bestResultNumberOfGuestFunctionsAmongFavs
                sumOfGuestS[controlGroups-1] += bestResultNumberOfGuestSlicesAmongFavs
                totalTime[controlGroups-1] += bestResultDurationAmongFavs

                for w in winners:
                    scores[w] += 1

                outputs.append("Control Set: {} Total Number of requests: {} Number of satisfied requests: {} Number of guests: {} Average Utilization: {}".format(
                                        controlGroups-1, numberOfReqs, maxSatisfiedRequestsInExperimentAmongFavs, bestResultNumberOfGuestSlicesAmongFavs, bestResultAvrgUtilAmongFavs))

            with open("results.txt", "a") as file1, open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open("guests.txt", "a") as file4, open("timeLine.txt", "a") as file5, open("scores.txt", "a") as file6:

                usageLine = ""
                satisfiedReqsline = ""
                guestFLine = ""
                guestSLine = ""
                timeLine = ""
                scoreLine = ""

                for c in range(0,controlGroups):
                    avrgUsage[c] = round(sumOfUsage[c] / numberOfExperiments, 2)
                    avrgSatisfiedReqs[c] = round(sumOfSatisfiedReqs[c] / numberOfExperiments, 2)
                    avrgGuestF[c] = round(sumOfGuestF[c] / numberOfExperiments, 2)
                    avrgGuestS[c] = round(sumOfGuestS[c] / numberOfExperiments, 2)
                    avrgTime[c] = round(totalTime[c] / numberOfExperiments / numberOfReqs, 4)

                    usageLine += str(avrgUsage[c]) + " "
                    satisfiedReqsline += str(avrgSatisfiedReqs[c]) + " "
                    guestFLine +=  str(avrgGuestF[c])  + " "
                    guestSLine += str(avrgGuestS[c]) + " "
                    timeLine += str(avrgTime[c]) + " "
                    scoreLine += str(scores[c]) + " "

                usageLine += "\n"
                satisfiedReqsline += "\n"
                guestFLine += "\n"
                guestSLine += "\n"
                timeLine += "\n"
                scoreLine += "\n"

                file2.write(usageLine)
                file3.write(satisfiedReqsline)
                file4.write(guestSLine)
                file5.write(timeLine)
                file6.write(scoreLine)

                for o in outputs:
                    print(o)
                    # Writing data to a file
                    file1.write(o + "\n")
                    #file1.writelines(L)
                    
    except Exception as e:
        print(e)

    with open("results.txt", "a") as file1, open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open(
            "guests.txt", "a") as file4, open("timeLine.txt", "a") as file5, open("scores.txt", "a") as file6:

        file1.write("\n")
        file2.write("\n")
        file3.write("\n")
        file4.write("\n")
        file5.write("\n")
        file6.write("\n")
