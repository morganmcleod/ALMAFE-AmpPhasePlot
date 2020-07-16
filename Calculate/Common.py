'''
Common calulation functions used by AmplitudeStability, PhaseStability
'''

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

def unwrapPhase(inputArray):
    '''
    Unwrap phase in the provided inputArray
    TODO: this won't deal with more than one zero crossing correctly
    :param inputArray:
    '''
    for i in range(len(inputArray)):
        if (inputArray[i] < 0):
            inputArray[i] += 360
