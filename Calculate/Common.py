'''
Common calulation functions used by AmplitudeStability, PhaseStability
'''
import numpy as np

def diffSquared(inputArray):
    '''
    Takes inputArray and returns an array consisting of the differences
    between adjacent elements, squared.    
    '''
    dX = []
    for i in range(len(inputArray) - 1):
        dX.append((inputArray[i + 1] - inputArray[i]) ** 2)
    return dX

def getAveragesArray(inputArray, K):
    '''
    returns averagesArray from inputArray, where each element of averagesArray
    contains the mean over non-overlapping groups of K samples of the inputArray.
    '''    
    averagesArray = []
    # N is the size of the input data array:
    N = len(inputArray)
    # K is the number of points to group and average:
    if K < 1:
        K = 1
    if K > N:
        K = N
    # M is number of groups:
    M = N // K
    for i in range(M):
        i0 = i * K            
        averagesArray.append(sum(inputArray[i0 : i0 + K]) / K)        
    return averagesArray

def getMinMaxArray(inputArray, K):
    '''
    returns minArray and naxArray from inputArray, where each element of the output arrays
    contain the min or max over non-overlapping groups of K samples of the inputArray.    
    '''
    minArray = []
    maxArray = []
    # N is the size of the input data array:
    N = len(inputArray)
    # K is the number of points to group and average:
    if K < 1:
        K = 1
    if K > N:
        K = N
    # M is number of groups:
    M = N // K
    for i in range(M):
        i0 = i * K            
        minArray.append(min(inputArray[i0 : i0 + K]))
        maxArray.append(max(inputArray[i0 : i0 + K]))        
    return minArray, maxArray

def getFirstItemArray(inputArray, K):
    '''
    returns firstItems from inputArray, where each element of firstItems
    contains the first element from each non-overlapping group of K samples of the inputArray.
    '''
    firstItems = []
     # N is the size of the input data array:
    N = len(inputArray)
    # K is the number of points to group and average:
    if K < 1:
        K = 1
    if K > N:
        K = N
    # M is number of groups:
    M = N // K
    for i in range(M):
        i0 = i * K            
        firstItems.append(inputArray[i0])
    return firstItems

def unwrapPhase(inputArray, period = 2 * np.pi):
    '''
    Unwrap phase in the provided inputArray
    :param inputArray:
    '''
    return np.unwrap(inputArray, period = period).tolist()
