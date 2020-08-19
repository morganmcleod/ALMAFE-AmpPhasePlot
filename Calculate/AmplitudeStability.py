from statistics import mean
import allantools
import bisect

class AmplitudeStability(object):
    '''
    Computes normalized non-overlapping Allan variance for a range of integration times.
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

    def calculate(self, dataSeries, tau0Seconds = 0.05, TMin = 0.05, TMax = 300):
        '''
        :param dataSeries: list of float, linear amplitudes to analyze
        :param tau0Seconds: integration time of the dataSeries
        :param TMin: float shortest integration time to plot
        :param TMax: float longest integration time to plot
        :return True if successful, false otherwise
                Updates self.xResult, self.yResult with computed Allan var trace.
        '''
        # clear anything kept from last run:
        self.__reset()
      
        # normalize the amplitudes to the mean because allantools doesn't do this:
        x0 = mean(dataSeries)
        dataSeries = [x / x0 for x in dataSeries]
        
        # adjust TMax and TMin
        N = len(dataSeries)
        dataDuration = N * tau0Seconds
        if (dataDuration < TMax):
            TMax = dataDuration
        if TMin < tau0Seconds:            
            TMin = tau0Seconds

        # compute longest integration time which can be made:        
        maxK = int(TMax / tau0Seconds) + 1
        
        # smallest number of groups M:
        minM = N // maxK
        if (minM < 2):
            # at least two groups are required
            minM = 2
            maxK = N // minM
        
        taus = []
        # make list of taus to calculate for:
        for K in range(1, maxK):        
            taus.append(K * tau0Seconds)
        
        # non-overlapping ADEV using allantools 'freq' mode.
        # https://github.com/aewallin/allantools
        (taus, adev, aderr, adn) = allantools.adev(dataSeries, 1 / tau0Seconds, data_type = "freq", taus = taus)
        
        # convert from numpy.ndarray to list:
        self.xResult = taus.tolist()
        
        # convert adevs to avars:
        self.yResult = []
        for y in adev:
            self.yResult.append(y ** 2)
        
        # convert adev errors to avars:
        self.yError = []
        for y in aderr:
            self.yError.append(y ** 2)
        
#         print("last point: {0} with error {1} and N={2}".format(self.yResult[-1], self.yError[-1], adn[-1]))
        return True
    
    def checkSpecLine(self, TMin, TMax, specMin, specMax):
        '''
        Test whether the calculated AVAR is below a given spec line.
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
            return self.yResult[iLower] <= specMin

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
        Private helper to find the indices corresponding to the provided integration time range.
        :param TMin: lower time limit to find.
        :param TMax: upper time limit for to find. Must be >= TMin.
        :return (iLower, iUpper): tuple of the first and last+1 indexes of self.xResult.
        '''
        iLower = bisect.bisect_left(self.xResult, TMin) if TMin else 0
        iUpper = bisect.bisect_right(self.xResult, TMax) if TMax else len(self.xResult)
        return (iLower, iUpper)        
        