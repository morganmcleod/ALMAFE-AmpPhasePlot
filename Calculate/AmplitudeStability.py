from statistics import mean
from .Common import getAveragesArray
from .allantools import adev as allantools_adev
import bisect
import operator
from math import sqrt

class AmplitudeStability(object):
    '''
    Computes non-overlapping Allan variance or Allan deviation for a range of time differencing intervals.
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

    def calculate(self, dataSeries, tau0Seconds = 0.05, TMin = 0.05, TMax = 300, normalize = True, calcAdev = False):
        '''
        :param dataSeries: list of float, linear amplitudes to analyze
        :param tau0Seconds: integration time of the dataSeries
        :param TMin: float shortest time differencing interval to plot
        :param TMax: float longest time differencing interval to plot
        :param normalize: If true, normalize to the mean amplitude
        :param calcAdev: If true, return ADEV instead of AVAR. 
        :return True if successful, false otherwise
                Updates self.xResult, self.yResult with computed Allan var trace.
        '''
        # clear anything kept from last run:
        self.__reset()
      
        # normalize the amplitudes to the mean because allantools doesn't do this:
        if normalize:
            x0 = mean(dataSeries)
            dataSeries = [x / x0 for x in dataSeries]
        
        # adjust TMax and TMin
        N = len(dataSeries)
        dataDuration = N * tau0Seconds
        if (dataDuration < TMax):
            TMax = dataDuration
        if TMin < tau0Seconds:            
            TMin = tau0Seconds

        # compute longest time differencing interval which can be made:        
        maxK = int(TMax / tau0Seconds) + 1
        
        # smallest number of groups M:
        minM = N // maxK
        if (minM < 2):
            # at least two groups are required
            minM = 2
            maxK = N // minM
        
        # make list of taus to calculate for:
        taus = [K * tau0Seconds for K in range(1, maxK)]
        
        # non-overlapping ADEV using allantools 'freq' mode.
        # https://github.com/aewallin/allantools
        (taus, adev, aderr, adn) = allantools_adev(dataSeries, 1 / tau0Seconds, data_type = "freq", taus = taus)
        
        # convert from numpy.ndarray to list:
        self.xResult = taus.tolist()
        
        if calcAdev:
            # return adevs and errors:
            self.yResult = adev.tolist()
            self.yError = aderr.tolist()
        else:
            # convert adevs and errors to variances:    
            self.yResult = [y ** 2 for y in adev]
            self.yError = [y ** 2 for y in aderr]
        
#         print("last point: {0} with error {1} and N={2}".format(self.yResult[-1], self.yError[-1], adn[-1]))
        return True
    
    def checkSpecLine(self, TMin, TMax, specMin, specMax):
        '''
        Test whether the calculated AVAR/ADEV is below a given spec line.
        Must be called after calculate()
        :param TMin:  Lower time (x) limit of spec line
        :param TMax:  Upper time (x) limit of spec line
        :param specMin: AVAR (y) value at TMin
        :param specMax: AVAR (y) value at TMax
        :return True/False
        '''
        # find the time range spanned:
        iLower, iUpper = self.__findTimeRange(TMin, TMax)
        
        # check for TMin == TMax or out of bounds:
        if iUpper <= iLower:
            iUpper = iLower + 1
            
        # exit early for single-point spec:
        if iUpper == iLower + 1:
            try:
                return self.yResult[iLower] <= specMin
            except:
                return self.yResult[iLower - 1] <= specMin

        # get the slope between the endpoints:        
        slope = (specMax - specMin) / (iUpper - iLower - 1)

        # compare result to spec, advancing the specY limit by slope at each step:
        specY = specMin
        for y in self.yResult[iLower:iUpper]:
            if y > specY:
                return False
            else:
                specY += slope
        return True
        
    def __findTimeRange(self, TMin, TMax):
        '''
        Private helper to find the indices corresponding to the provided time differencing interval range.
        :param TMin: lower time limit to find.
        :param TMax: upper time limit for to find. Must be >= TMin.
        :return (iLower, iUpper): tuple of the first and last+1 indexes of self.xResult.
        '''
        iLower = bisect.bisect_left(self.xResult, TMin) if TMin else 0
        iUpper = bisect.bisect_right(self.xResult, TMax) if TMax else len(self.xResult)
        return (iLower, iUpper)        
        