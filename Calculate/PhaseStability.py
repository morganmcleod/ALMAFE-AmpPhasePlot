from Calculate.Common import getAveragesArray, unwrapPhase
from math import sqrt

class PhaseStability(object):
    '''
    Computes the 2-point Allan standard deviation with a fixed averaging time, 
    tau0 and intervals T between TMin and TMax seconds.   
    If tau0 < TMin, the data will first be averaged into intervals of approximately TMin.  
    Equation from ALMA-80.04.00.00-005-B-SPE:
        sigma^2(2,T,tau) = 0.5 * < [phi.tau(t + T) - phi.tau(t)] ^ 2 >  
        where phi.tau = the average of the absolute or differential phase over time tau = 10 seconds.
        < ... > means the average over the data sample which should extend to 10 or 20 x Tmax seconds.    
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__reset()
    
    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.xResult = None
        self.yResult = None  
        self.yError = None  
        self.freqRFGHz = None

    def calculate(self, dataSeries, tau0Seconds = 1.0, TMin = 10.0, TMax = 300.0, freqRFGHz = None):
        '''
        :param dataSeries:  list of float degrees phases to analyze
        :param tau0Seconds: integration time of the dataSeries
        :param TMin: float shortest integration time to plot
        :param TMax: float longest integration time to plot
        :param freqRFGHz:  if provided, the Allan dev yResult will be returned in fs rather than degreees
        :return True if successful, otherwise False
        '''
        # clear anything kept from last run:
        self.__reset()
        self.freqRFGHz = freqRFGHz if freqRFGHz and freqRFGHz > 0.0 else None
        
        # number of whole tau0 intervals in TMin: 
        NMin = int(TMin / tau0Seconds)

        # if we have less than 2 * NMin samples, abort:
        if len(dataSeries) < (2 * NMin):
            return False

        # compute new TMin rounded down to whole tau0 intervals:
        TMin = tau0Seconds * NMin        

        # before processing, make sure that the phase data doesn't wrap around:
        unwrapPhase(dataSeries)
        
        # If more than one sample fits in the new TMin
        if NMin > 1:
            # integrate TMin worth of samples: 
            averagesArray = getAveragesArray(dataSeries, NMin)
            NMin = 1
        else:
            # otherwise use the original array: 
            averagesArray = dataSeries 

        # check TMax parameter in light of above adjustments: 
        dataDuration = len(averagesArray) * TMin

        # TMax can be no longer than the data set:
        if (TMax > dataDuration):
            TMax = dataDuration            

        NMax = int(TMax / TMin)
   
        self.xResult = []
        self.yResult = []
        self.yError = []
        for K in range(NMin, NMax + 1):
            # calculate T for this iteration and save to the output time array:
            self.xResult.append(K * TMin)
            # calculate ADev for this iteration and save to the output Allan array:
            adev, aderr, adn = self.ADev(averagesArray, K)
            self.yResult.append(adev)
            self.yError.append(aderr)
        return True
        
    def ADev(self, inputArray, K):
        '''
        Returns the 2-point Allan standard deviation of an inputArray
        ADev = sqrt(0.5 * < [phi.tau(t + T) - phi.tau(t)] ^ 2 >) where
        phi.tau = the average of the absolute or differential phase over time tau.
        < ... > means the average over the data sample
        If freqRFGHz>0 compute devs converted to fs at the given frequency.
        '''
        # conversion factor for fs per degree:
        fsDeg = None
        if self.freqRFGHz:
            period = 1.0 / (float(self.freqRFGHz) * 1.0e9)
            fsDeg = (period * 1.0e15) / 360.0        
        
        M = len(inputArray)
        total = 0
        for aIndex in range(M - K):
            # accumulate a sum of squares of differences...
            diff = inputArray[aIndex] - inputArray[aIndex + K]
            # optionally converted to fs:
            if (fsDeg):
                diff *= fsDeg
            total += diff ** 2.0
        
        # and multiply by 0.5, divide by the number of differences, take the square root for standard deviation: 
        numDiffs = M - K - 1
        adev = sqrt(0.5 * total / numDiffs)        
        aderr = adev / sqrt(numDiffs)
        adn = numDiffs
        return (adev, aderr, adn)
