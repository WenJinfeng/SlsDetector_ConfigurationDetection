from collections import Counter
from GeneralMethod import uniRepAll, transforRepPattern
import itertools



# implement FP-Growth
# part 1 : construct node classes
class treeNode:

    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue 
        self.count = numOccur 
        self.nodeLink = None 
        self.parent = parentNode 
        self.children = {} 
    
    def inc(self, numOccur):

        self.count += numOccur

    def disp(self, ind=1):
        for child in self.children.values():
            child.disp(ind + 1) 


# part 2 : Raw data creation and processing
from collections import OrderedDict

def createInitSet(dataSet):

    retDict=OrderedDict() # retDict = {}
    for trans in dataSet:
       
        retDict[frozenset(trans)] = 1
    return retDict

# part 3 : create FP tree
def createTree(dataSet,  minSup=1):

    headerTable = {}  
    for trans in dataSet:  
        for item in trans:     
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    for k in list(headerTable.keys()): 
        if headerTable[k] < minSup:
            del (headerTable[k]) 
   
    # start to construct FP tree
    freqItemSet = set(headerTable.keys())  

    if len(freqItemSet) == 0:
        return None, None

    for k in headerTable: 
        headerTable[k] = [headerTable[k], None] 
    retTree = treeNode('Null Set', 1, None) 
    
    for tranSet, count in dataSet.items(): 
       
        localD = {} 
        for item in tranSet:
            if item in freqItemSet:
                
                localD[item] = headerTable[item][0]
       
        if len(localD) > 0: 
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]

            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable

    
def updateTree(items, inTree, headerTable, count):

    if items[0] in inTree.children:
        
        inTree.children[items[0]].inc(count)
    else:
       
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
       
        if headerTable[items[0]][1] is None: 
            headerTable[items[0]][1] = inTree.children[items[0]] 
        else:
            
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:
        
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)



def updateHeader(nodeToTest, targetNode):

    while nodeToTest.nodeLink is not None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode



# part 4 ：mine frequent item sets
def ascendTree(leafNode, prefixPath):

    if leafNode.parent is not None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)


def findPrefixPath(basePat, treeNode):

    condPats = {}
    while treeNode is not None: 
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1: 
           
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        
        treeNode = treeNode.nodeLink
        
    return condPats


# part 5 : Recursive search for frequent item sets
def mineTree(inTree, headerTable, minSup, preFix, freqItemList):

    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: str(p[1]))]

    for basePat in bigL:
        newFreqSet = preFix.copy() 
        newFreqSet.add(basePat)
        
        freqItemList.append(newFreqSet)
        

        condPathBases = findPrefixPath(basePat, headerTable[basePat][1])
        myCondTree, myHead = createTree(condPathBases, minSup)
        
        if myHead is not None:
           
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)

# mine coarse-gained configuration dependencies
def mainAllRuleSAMCorse(directoryPath, threshold):

    simpData = loadSimpDatSAMCorse(directoryPath) 

    initSet = createInitSet(simpData)
    minSup =threshold * len(simpData)

    print(minSup)

    myFPtree, myHeaderTab = createTree(initSet, minSup)
    myFPtree.disp()
    freqItemList = []
    mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItemList)
    newfreqItemList = []
    print(freqItemList)
    for item in freqItemList:
        if ("Transform" not in item) and ("AWSTemplateFormatVersion" not in item) and ("Description" not in item):
            flag = 0
            for field_i in item:
                rootname = field_i.split(".")[0]
                if rootname != "Outputs" and rootname != "Parameters" and "Description" not in field_i:
                    flag = flag + 0
                else:
                    flag = flag + 1
            if flag==0:
                newfreqItemList.append(item)

    print(len(freqItemList))
    print(len(newfreqItemList))


    
    left,right = handlefreqItemListSAMCorse(newfreqItemList, simpData)

    return left, right


import concurrent.futures
import itertools

import itertools

import itertools

def handlefreqItemListSAMCorse(freqItemList, simpData):
    saveleft = []
    saveright = []

    
    simpData_sets = [set(data) for data in simpData]

    I1= 1

    for tmp in freqItemList:
        print(f"processing {I1} tmp, total {len(freqItemList)}, doing {(I1)/len(freqItemList)*100}%")
        I1 = I1 +1
        combinations = generate_combinations(tmp)

        I2 = 1

        for left, right in combinations:

            print(f"processing {I2} combination, total {len(combinations)} doing {(I2)/len(combinations)*100}%")
            I2 = I2 +1 
            left_set = set(left)
            right_set = set(right)
            tolen = len(left) + len(right)

           
            if tolen > 1 and 'Transform' not in left_set and 'Transform' not in right_set and \
               'AWSTemplateFormatVersion' not in left_set and 'AWSTemplateFormatVersion' not in right_set:
                flag = 0
                for data_i_set in simpData_sets:
                    if left_set.issubset(data_i_set):
                        if right_set.issubset(data_i_set):
                            flag += 0
                        else:
                            flag += 1
                if flag == 0:
                    saveleft.append(left)
                    saveright.append(right)

    
    filter_saveleft = []
    filter_saveright = []
    seen_left = {} 

    for left, right in zip(saveleft, saveright):
        left_set = frozenset(left)
        right_set = frozenset(right)
        
        if left_set not in seen_left:
            seen_left[left_set] = right_set
            filter_saveleft.append(left)
            filter_saveright.append(right)
        else:
            if not right_set.issubset(seen_left[left_set]):
                filter_saveleft.append(left)
                filter_saveright.append(right)

    
    rootContentleft = "correlationleftCoarse"
    rootContentright = "correlationrightCoarse"

    with open(f"Patterns/sam_{rootContentleft}.txt", "w") as f_left:
        f_left.write("\n".join("+++".join(left) for left in filter_saveleft))

    with open(f"Patterns/sam_{rootContentright}.txt", "w") as f_right:
        f_right.write("\n".join("+++".join(right) for right in filter_saveright))

    print(len(filter_saveleft))

    return filter_saveleft, filter_saveright




# data processing 
def loadSimpDatSAMCorse(directoryPath):

    
    simpData = addEntryValueRepSAMCorse(directoryPath)
   
    return simpData

def addEntryValueRepSAMCorse(directoryPath):
    total_flat_config = uniRepAll(directoryPath)
    entryAll = []
    for file_i in total_flat_config:
        entryfile = []
        flat_config_key_new, flat_config_value_new = transforRepPattern(file_i)
        for index in range(len(flat_config_key_new)):
            tmp = "{}".format(flat_config_key_new[index])
            entryfile.append(tmp)
        entryfile = list(set(entryfile))
        entryAll.append(entryfile)
    return entryAll

import itertools

def generate_combinations(elements):
    all_combinations = []
    seen_right = set() 

    for r in range(1, len(elements)):
        left_combinations = itertools.combinations(elements, r)
        
        for left in left_combinations:
            right = tuple(sorted(e for e in elements if e not in left))
            
            if right not in seen_right: 
                all_combinations.append((left, right))
                seen_right.add(right)  
        
    return all_combinations


def handlefreqItemListSAMFine(freqItemList, simpData):
    saveleft = []
    saveright = []

   
    simpData_sets = [set(data) for data in simpData]

    I1= 1

    for tmp in freqItemList:
       
        I1 = I1 +1
        combinations = generate_combinations(tmp)

        I2 = 1

        for left, right in combinations:

            print(f"processing {I1} tmp, total {len(freqItemList)} doing {(I1)/len(freqItemList)*100}%, doing {I2} combination, total {len(combinations)} doing {(I2)/len(combinations)*100}%")
            I2 = I2 +1 
            left_set = set(left)
            right_set = set(right)
            tolen = len(left) + len(right)

            
            if tolen > 1 and 'Transform=AWS::Serverless-2016-10-31' not in left_set and 'Transform=AWS::Serverless-2016-10-31' not in right_set and \
               'AWSTemplateFormatVersion=2010-09-09' not in left_set and 'AWSTemplateFormatVersion=2010-09-09' not in right_set:
                flag = 0
                for data_i_set in simpData_sets:
                    if left_set.issubset(data_i_set):
                        if right_set.issubset(data_i_set):
                            flag += 0
                        else:
                            flag += 1
                if flag == 0:
                    saveleft.append(left)
                    saveright.append(right)

    
    filter_saveleft = []
    filter_saveright = []
    seen_left = {}  

    for left, right in zip(saveleft, saveright):
        left_set = frozenset(left)
        right_set = frozenset(right)
        
        if left_set not in seen_left:
            seen_left[left_set] = right_set
            filter_saveleft.append(left)
            filter_saveright.append(right)
        else:
            if not right_set.issubset(seen_left[left_set]):
                filter_saveleft.append(left)
                filter_saveright.append(right)

    
    rootContentleft = "correlationleftFine"
    rootContentright = "correlationrightFine"

    with open(f"Patterns/sam_{rootContentleft}.txt", "w") as f_left:
        f_left.write("\n".join("+++".join(left) for left in filter_saveleft))

    with open(f"Patterns/sam_{rootContentright}.txt", "w") as f_right:
        f_right.write("\n".join("+++".join(right) for right in filter_saveright))

    print(len(filter_saveleft))

    return filter_saveleft, filter_saveright


def mainAllRuleSAMFine(directoryPath,threshold):
    
    simpData = loadSimpDatSAM(directoryPath) 
    

    initSet = createInitSet(simpData)
    minSup = threshold * len(simpData)
    
    print(minSup)

    myFPtree, myHeaderTab = createTree(initSet, minSup)
    myFPtree.disp()
    freqItemList = []
    mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItemList)
    print(freqItemList)
   

    newfreqItemList = []
    for item in freqItemList:
    
        flag = 0
        for field_i in item:
            tmp = field_i.split("=")
            rootname = tmp[0].split(".")[0]
            if rootname != "Outputs" and rootname != "Parameters" and tmp[0] != "Transform" and tmp[0] != "AWSTemplateFormatVersion" and tmp[0] != "Description" and "Description" not in tmp[0]:
                flag = flag + 0
            else:
                flag = flag + 1
        if flag==0:
            newfreqItemList.append(item)
    
    print(len(freqItemList))
    print(len(newfreqItemList))

    
    left,right = handlefreqItemListSAMFine(newfreqItemList, simpData)

    return left, right
    



def loadSimpDatSAM(directoryPath):
    simpData = addEntryValueRepSAM(directoryPath)
    return simpData


def addEntryValueRepSAM(directoryPath):
    total_flat_config = uniRepAll(directoryPath)
    entryAll = []
    for file_i in total_flat_config:
        entryfile = []
        flat_config_key_new, flat_config_value_new = transforRepPattern(file_i)
        for index in range(len(flat_config_key_new)):
            tmp = "{}={}".format(flat_config_key_new[index], flat_config_value_new[index])
            entryfile.append(tmp)
        entryfile = list(set(entryfile))
        entryAll.append(entryfile)
    return entryAll



              
if __name__ == "__main__":

    # mine configuration dependencies
    directoryPath = "Dataset"
    # threshold = 0.1
    threshold = 0.05
    # threshold = 0.01

    
    # mine coarse-gained configuration dependencies
    mainAllRuleSAMCorse(directoryPath, threshold)

    # mine fine-gained configuration dependencies
    mainAllRuleSAMFine(directoryPath, threshold)