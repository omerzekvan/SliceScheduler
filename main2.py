# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import ast
#import pgdb
import slice
import copy
import random
import time
import concurrent.futures
#import numpy as np


#from psycopg2.extensions import register_adapter#, AsIs

#def addapt_numpy_float64(numpy_float64):
#    return AsIs(numpy_float64)
#def addapt_numpy_int64(numpy_int64):
#    return AsIs(numpy_int64)
#register_adapter(np.float64, addapt_numpy_float64)
#register_adapter(np.int64, addapt_numpy_int64)

# criteria = 0 # Network Service capacity
criteria = 1 # Priority of Network Slice
Re = 2
NFavailability = 99.9 # In fact np.float128(0.999)

global delayAware
delayAware = False

global TServices
TServices = []

global totalUnderutilized
totalUnderutilized = 0

global control

functionsCatalog = [{"id": 0, "name":'AMF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 1, "name": 'AUSF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 2, "name": 'NEF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 3, "name": 'NRF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 4, "name": 'NSSF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 5, "name": 'PCF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 6, "name":'SMF', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 7, "name": 'UDM', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 8, "name": 'UDR', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 9, "name": 'UPF', "cpu": 8, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 10, "name": 'CU', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0},
                    {"id": 11, "name": 'DU', "cpu": 2, "availability": NFavailability, "reqCount": 0, "lowReqCount": 0}
                    ]
servicesCatalog = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11]]
sliceRequests = [{"services": [0, 1], "priority": 1, "availability": 0.99, "bw": 0.5, "delay": 100},
                 {"services": [0, 1], "priority": 2, "availability": 0.9, "bw": 0.5, "delay": 10},
{"services": [0, 1], "priority": 2, "availability": 0.99, "bw": 0.5, "delay": 100},
{"services": [0, 1], "priority": 2, "availability": 0.9, "bw": 0.5, "delay": 10},
{"services": [0, 1], "priority": 1, "availability": 0.99, "bw": 0.5, "delay": 10},
                 {"services": [0, 1], "priority": 2, "availability": 0.99, "bw": 0.5, "delay": 10}]

linkCapacity = 10
oneNodeCPU = 60

# Konuşan iki pod aynı node içindeyse gecikme 0, değilse gecikme 3 ms olarak varsayıldı.
constantDelay = 10

originalNodeCapacities = sorted([{"cap": oneNodeCPU-4*i, "ind": i} for i in range(6)], key=lambda item: item["cap"], reverse=True)
#originalNodeCapacities = sorted([{"cap": oneNodeCPU, "ind": i} for i in range(6)], key="cap", reverse=True)
#originalNodeCapacities = sorted([oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True) #, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True)
nodeCapacity = sorted([{"cap": oneNodeCPU-4*i, "ind": i} for i in range(6)], key=lambda item: item["cap"], reverse=True)
#nodeCapacity = sorted([oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True) #, oneNodeCPU, oneNodeCPU, oneNodeCPU, oneNodeCPU], reverse=True)
N = len(nodeCapacity)

#global leastCapacityNode
#leastCapacityNode = False

# Make nodes with zero load
def resetNodes():
#    for index, value in enumerate(originalNodeCapacities):
#        nodeCapacity[index] = value
    # nodeCapacity = []
    #global nodeCapacity
    #nodeCapacity = sorted([{"cap": oneNodeCPU-4*i, "ind": i} for i in range(6)], key=lambda item: item["cap"], reverse=True)
    global nodes
    #nodes = [slice.Node(i, oneNodeCPU) for i in range(N)]
    nodes = slice.Node.sort_by_capacity([slice.Node(i, oneNodeCPU-4*i) for i in range(N)])
    
    b = 1

resetNodes()

# Create a list of rows, where each row is filled with the same value
originalBWMatrix = [[linkCapacity for _ in range(10)] for _ in range(10)]
liveBWMatrix = [[linkCapacity for _ in range(10)] for _ in range(10)]


# Failure probability of a physical node
hN = 0.001
HighAv = 99.99

FFunctions = []

def generateSliceRequests(numberOfRequests : int):
    try:
        # with open("sliceRequests.txt", "w") as file:

        global sliceRequests
        sliceRequests = []

        for l in range(0,numberOfRequests):
            #print("L: {}".format(l))

            # Number of NFs in a network slice
            length = random.randint(3,10)
            vnfChain = []
            remainingVNFs = [i for i in range(10)]
            #print(remainingVNFs)

            for len in range(0,length):
                #print("len: {}".format(len))
                whichVNF = random.randint(0,9-len)
                #print("whichVNF: {}".format(whichVNF))

                indexOfVNF = remainingVNFs.pop(whichVNF)
                vnfChain.append(indexOfVNF)

            #print(vnfChain)
            priority = random.randint(1, 2)
            bwRand = random.randint(1, 5)
            delay = random.randint(10, 20) # in milliseconds

            #av = random.randint(80, 99)/100

            #In fact av = np.float128(99.999/100) if priority == 1 else 0.9
            av = HighAv if priority == 1 else 90
            bw = bwRand * 0.1

            # file.write("{\"services\": , \"priority\": {}, \"availability\": {}}".format( str(priority), str(av)))
            #line = "(\"services\": {} , \"priority\": {}, \"availability\": {})\n".format(str(vnfChain), str(priority), str(av))
            #print("Priority: {}".format(priority))
            #print("Av: {}".format(av))

            #print("Bw: {}".format(bw))
            #line = f"{'services': {str(vnfChain)} , 'priority': {str(priority)}, 'availability': {float(av)}}\n"
            line = "{\"id\": %d ,\"services\": %s , \"priority\": %d, \"availability\": %.2f, \"bandwidth\": %.1f}\n" % (l+1, str(vnfChain), priority, av, bw)
            #print(f'Only {i:10d} replicas out of {replicasNeeded} are successfully onboarded')

            sl = slice.Slice(l+1, vnfChain, priority, av, bw, delay)
            #sliceRequests.append(ast.literal_eval(line))
            sliceRequests.append(sl)

                #file.write(line)

    except Exception as e:
        print("Exception: {}".format(e))
    return

def countCNFRequests(sliceRequests=[]):


    for l in sliceRequests:
        for s in l.services:
            if l.priority == 1:
                functionsCatalog[s]["reqCount"] += 1
            else:
                functionsCatalog[s]["lowReqCount"] += 1


def rateSlices(ratinglevel):
    if ratinglevel == -1:
        for l in sliceRequests:
            #prior = 10 if l.priority == 1 else 2
            #l.points = 10**6 * prior
            l.points = 0
            for s in l.services:
                l.points += 10**3 * functionsCatalog[s]["cpu"]       
    elif ratinglevel == 0:
    #     for l in sliceRequests:
    #         size = len(l.services)
    #         #prior = 10 if l.priority == 1 else 2
    #         #l.points = 10**6 * prior
    #         l.points = 10 ** 6 * l.priority
    #         for s in l.services:
    #             l.points -= (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    # elif ratinglevel == 1:
    #     for l in sliceRequests:
    #         size = len(l.services)
    #         # prior = 10 if l.priority == 1 else 2
    #         # l.points = 10**6 * prior
    #         l.points = 10 ** 6 * l.priority
    #         for s in l.services:
    #             l.points += (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    # elif ratinglevel == 2:
        for l in sliceRequests:
            #prior = 10 if l.priority == 1 else 2
            #l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10**3 * functionsCatalog[s]["cpu"]
    elif ratinglevel == 3:
        for l in sliceRequests:
            size = len(l.services)
            # prior = 10 if l.priority == 1 else 2
            # l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10 ** 3 * functionsCatalog[s]["cpu"] + (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 4:
        for l in sliceRequests:
            size = len(l.services)
            # prior = 10 if l.priority == 1 else 2
            # l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10 ** 3 * functionsCatalog[s]["cpu"] - (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 5:
        for l in sliceRequests:
            size = len(l.services)
            # prior = 10 if l.priority == 1 else 2
            # l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l.priority == 1:
                    l.points -= (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
                else:
                #if l.priority == 2:
                    l.points += (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
    elif ratinglevel == 6:
        for l in sliceRequests:
            size = len(l.services)
            # prior = 10 if l.priority == 1 else 2
            # l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l.priority == 1:
                    l.points += (functionsCatalog[s]["reqCount"] + functionsCatalog[s]["lowReqCount"]) /size
                else:
                #if l.priority == 2:
                    l.points -= (functionsCatalog[s]["reqCount"]  + functionsCatalog[s]["lowReqCount"]) / size
    elif ratinglevel == 7:
        for l in sliceRequests:
            size = len(l.services)
            # prior = 10 if l.priority == 1 else 2
            # l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l.priority == 1:
                    l.points -= functionsCatalog[s]["lowReqCount"] / size
                else:
                    # if l.priority == 2:
                    l.points -= functionsCatalog[s]["reqCount"] / size
    elif ratinglevel == 8:
        for l in sliceRequests:
            size = len(l.services)
            # prior = 10 if l.priority == 1 else 2
            # l.points = 10**6 * prior
            l.points = 10 ** 6 * l.priority
            for s in l.services:
                l.points += 10 ** 3 * functionsCatalog[s]["cpu"]
                if l.priority == 1:
                    l.points += functionsCatalog[s]["lowReqCount"] / size
                else:
                    # if l.priority == 2:
                    l.points += functionsCatalog[s]["reqCount"] / size

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


# Returns the index of the item with minimum value. Returns the minimum index in case of a tie.
def findMinimum(array=[]):
    minimum = oneNodeCPU
    for a in array:
        if minimum > a: minimum = a
    return minimum

# node = -1, Tüm makinelerde anlamındadır.
def findHost(nfID, dilim, node = -1):

    NF = functionsCatalog[nfID]
    for t in TServices:

        for d in t.fDeployments:
            # If this is the service we are looking for and has enough capacity use it
            if d.type == NF["name"]:
                if d.residualCPU >= NF["cpu"]:
                    
                    if node == -1:
                        t.hostedSlices.append(dilim.id)
                        if delayAware == True and dilim.delay < calculateDelay(dilim):
                            t.hostedSlices.pop()
                            continue
                                
                        t.guests += 1
                        # foundT = True    
                    
                        totalUnderutilized -= NF["cpu"]
                        # isGuest = True
                        d.residualCPU -= NF["cpu"]

                        return 1 # Bu bir misafir (Guest) ve artık foundT True olmalı.
                    else:
                        for p in d.pods:
                            if p.node == node:
                                t.hostedSlices.append(dilim.id)
                                if delayAware == True and dilim.delay < calculateDelay(dilim):
                                    t.hostedSlices.pop()
                                    continue
                                    
                                t.guests += 1
                                # foundT = True    
                            
                                totalUnderutilized -= NF["cpu"]
                                # isGuest = True
                                d.residualCPU -= NF["cpu"]

                                return 1 # Bu bir misafir (Guest) ve artık foundT True olmalı.

    return 0

# Onboarding a function means there is not other shared function that can be used
# Daha sonra targetAv kaldırılabilir. Bu bilgi zaten slice içinde var.
def onboard(networkFunction, targetAv, dilim, leastCapacityNode=False):

    functionAv = networkFunction.availability
    Rcpu = networkFunction.cpu
    global delayFail
    delayFail = False
    hostingResult = 0

    replicasNeeded = computeNumberOfReplicasNeeded(functionAv, targetAv)

    if replicasNeeded == 0:
        #print("The number of replicas needed is too high")
        return 0
    
    if leastCapacityNode==True:
        # Sort nodeCapacity in ascending Cn order

        #sortedNodeCapacity = sorted(nodeCapacity, key=lambda item: item["cap"])
        global nodes
        nodes = slice.Node.sort_by_remCapacity(nodes)

    #else:
    #    sortedNodeCapacity = nodeCapacity

    i = 0
    for n in nodes:


        #if leastCapacityNode:
        #    currentNodeCapacity = findMinimum(nodeCapacity)
        #    ind = nodeCapacity.index(currentNodeCapacity)
        #else:
        #    currentNodeCapacity = nodeCapacity[n]
        #    ind = n

        #currentNodeCapacity = sortedNodeCapacity[n]["cap"]

        #ind = sortedNodeCapacity[n]["ind"]
        # Current capacity is enough, so onboard the NF
        #if currentNodeCapacity >= Rcpu:

        # Her iki posun da gecikme sınırı altında olacak şekilde dağıtım yapar. Eğer bu istenmiyorsa gevşetilmelidir.

        if (control%12 == 8 or control%12 == 11) and dilim.priority == 2:
            
            hostingResult = findHost(networkFunction.id, dilim, n.ID)
            #if n.remCapacity >= Rcpu and (delayAware == False or dilim.delay > totalD): 
            if hostingResult == 1:
                # i += 1
                return -2

        if  replicasNeeded > i and n.remCapacity >= Rcpu:
            networkFunction.deployedNodes.append(n.ID)

            if delayAware == True:
                totalD = calculateDelay(dilim)
                if dilim.delay < totalD:
                    networkFunction.deployedNodes.pop()
                    
                    delayFail = True
                    continue
            #nodeCapacity[ind]["cap"] -= Rcpu
            n.remCapacity -= Rcpu

            i += 1

            networkFunction.pods.append(slice.Pod(networkFunction.type, networkFunction.cpu, n.ID))

        if replicasNeeded <= i:
            #print(f'{i:10d} replicas onboarded')
            networkFunction.setReplicas(replicasNeeded)

            # db.addNodesToFunc(networkFunction.id, networkFunction.deployedNodes)


            networkFunction.totalCPU = networkFunction.cpu * i
            networkFunction.residualCPU = networkFunction.cpu * (i - 1)

            return i

    networkFunction.totalCPU = networkFunction.cpu * i
    networkFunction.residualCPU = networkFunction.cpu * (i-1)

    #print(f'Only {i:10d} replicas out of {replicasNeeded} are successfully onboarded')
    if delayFail == True: return -1

    return 0

def updateNodes():
    #resetNodes()
    #slice.Node.reset_nodes(nodes)
    global nodes
    #nodes = [slice.Node(i, oneNodeCPU) for i in range(N)]
    resetNodes()

    global FFunctions 
    for r in FFunctions:
        #cpuNeed = r[1]
        deployedNodes = r.deployedNodes
        for d in deployedNodes:
            nodes[d].remCapacity -= r.cpu
            
def deleteGuests(sliceId):
    for t in TServices:
        for index, hosted in enumerate(t.hostedSlices):
            if hosted == sliceId:
                del t.hostedSlices[index]

                t.guests -= 1
                
                totalUnderutilized += t.capacity

                t.fDeployments[0].residualCPU += t.capacity

    return

def deleteFunctions(serviceId):
    global FFunctions
    
    for index, r in enumerate(FFunctions):
        if (r.hostServiceId == serviceId):
          del FFunctions[index]

def totalRemainingCapacity():
    total = 0
    for n in nodes:
        total += n.remCapacity

    return total

def calculateDelay(slice):

    totalDelay = 0
    global source, dest
    source = -1
    dest = -1
    sID = slice.id
    

    #{"services": [0, 1], "priority": 2, "availability": 0.9, "bw": 0.5}

    for s in slice.services:
        foundInTServices = False
        for t in TServices:
            for h in t.hostedSlices:
                if h == sID:
                    functionsList = servicesCatalog[s]
                    for f in functionsList:
                        for ff in t.fDeployments:
                            if functionsCatalog[f]["name"] == ff.type: 
                                for p in ff.pods:
                                    dest = p.node
                                    if source > -1 and source != dest: totalDelay += constantDelay
                                    if totalDelay > slice.delay: return totalDelay # Dilim bu gecikmeyi kabul etmiyorsa çık
                                    source = p.node
                                    foundInTServices = True
                                    break # Gecikmenin daha da optimize edilmesi için diğer poda da bakılmalı. Burada atlanıyor.
                                if foundInTServices == True: 
                                    break # Burada sID barınıyorsa diğer servislere bakmaya gerek yok
                    break # Burada sID barınıyorsa diğer dilimlere bakmaya gerek yok
            if foundInTServices == True: break # Aradığımız servisi bulduk
    
    return totalDelay

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    maxNumberOfReqs = 500
    numberOfExperiments = 600

    try:
        with open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open("timeLine.txt", "a") as file5, open("underutil.txt", "a") as file10:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            # ... (keep your existing headers for files)

            for numberOfReqs in range(20, maxNumberOfReqs+1, 20):
                outputs = []
                sumOfUsage = []
                sumOfUnderUtil = []
                sumOfSatisfiedReqs = []
                totalTime = []
                scores = []
                avrgUsage = []
                avrgUnderUtil = []
                avrgSatisfiedReqs = []
                avrgTime = []

                for experiment in range(numberOfExperiments):
                    generateSliceRequests(numberOfReqs)

                    # Start with a minimal number of nodes
                    minNodes = 1
                    maxNodes = len(nodes)  # Assuming 'nodes' is defined somewhere
                    nodesNeeded = minNodes

                    while True:
                        resetNodes()  # Reset node capacities for each new test
                        nodes = [slice.Node(capacity=100) for _ in range(nodesNeeded)]  # Example: each node has 100 capacity units
                        satisfiedRequests = 0
                        totalUnderutilized = 0

                        startTime = time.time()

                        # Sort slices based on priority or other criteria if needed
                        sortedSlices = sorted(sliceRequests, key=lambda d: d.priority)

                        for r in sortedSlices:
                            if not placeSlice(r, nodes, nodesNeeded):
                                # If placement fails, increase the number of nodes
                                if nodesNeeded < maxNodes:
                                    nodesNeeded += 1
                                    break
                                else:
                                    # All possible nodes used, stop trying
                                    break
                            else:
                                satisfiedRequests += 1

                        if satisfiedRequests == len(sortedSlices) or nodesNeeded > maxNodes:
                            # All requests satisfied or we've reached max nodes
                            break

                    endTime = time.time()
                    duration = endTime - startTime

                    # Here you would calculate utilization, underutilization, etc., similar to your original code
                    # but now based on the minimal node count that satisfied all requests

                    # Append to lists for averaging later
                    # Note: Adjust these based on how you calculate these metrics with minimal nodes
                    sumOfUsage.append(calculateUsage(nodes))
                    sumOfUnderUtil.append(calculateUnderUtilization(nodes))
                    sumOfSatisfiedReqs.append(satisfiedRequests)
                    totalTime.append(duration)

                    outputs.append(f"Experiment: {experiment}, Nodes needed: {nodesNeeded}, Satisfied: {satisfiedRequests}")

                # Calculate averages and write to files as before
                # ...

    except Exception as e:
        print(e)

    with open("usage.txt", "a") as file2, open("satisfied.txt", "a") as file3, open("timeLine.txt", "a") as file5, open("underutil.txt", "a") as file10:

        file2.write("\n")
        file3.write("\n")
        file5.write("\n")
        file10.write("\n")
