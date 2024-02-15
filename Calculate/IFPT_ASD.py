"""
This script, along with allantools.py are deployed to the ALMA BE IFP Test set
"""

import numpy as np
try:
    from allantools import adev as allantools_adev
except:
    from .allantools import adev as allantools_adev
    
def AllanDev(config, data):
    """Allan standard deviation to be called from IFP Testset LabVIEW code

    :param Tuple[float, float, float, float] config:
        delta_t: the sampling interval, seconds
        tau: the step size for T. If delta_t < tau, the data will first be averaged
             and if necessary tau adjusted to the nearest integer multiple of delta_t
        t_start, t_stop: the range of T over which to calculate
    :param List[float] data: the raw data samples
    :return Tuple[List[float], List[float], list[float]]:
        taus: the X axis of the Allan deviation plot
        adev: they Y axis of the plot
        aderr: the error bars for adev        
    """
    # get input parameters
    delta_t = config[0]
    tau = config[1]
    t_start = config[2]
    t_stop = config[3]

    # normalize
    x0 = np.mean(data)
    data = [x / x0 for x in data]

    # boxcar average data:
    if delta_t < tau:
        K = tau // delta_t + 1
        data = getAveragesArray(data, K)
        tau = K * delta_t

    # adjust t_stop and t_start
    N = len(data)
    dataDuration = N * tau
    if (dataDuration < t_stop):
        t_stop = dataDuration
    if t_start < tau:            
        t_start = tau

    # compute longest time differencing interval which can be made:        
    maxK = int(t_stop / tau) + 1
        
    # smallest number of groups M:
    minM = N // maxK
    if (minM < 2):
        # at least two groups are required
        minM = 2
        maxK = N // minM
    
    # make list of taus to calculate for:
    taus = [K * tau for K in range(1, maxK)]
    
    # non-overlapping ADEV using allantools 'freq' mode.
    # https://github.com/aewallin/allantools
    (taus, adev, aderr, adn) = allantools_adev(data, 1 / tau, data_type = "freq", taus = taus)
    
    # convert from numpy.ndarray to list:
    return (taus.tolist(), adev.tolist(), aderr.tolist())
    
def getAveragesArray(inputArray, K):
    '''
    returns averagesArray from inputArray, where each element of averagesArray
    contains the mean over non-overlapping groups of K samples of the inputArray.
    '''    
    averagesArray = []
    # N is the size of the input data array:
    N = len(inputArray)
    # K is the number of points to group and average:
    K = int(K)
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
