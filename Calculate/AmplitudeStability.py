from statistics import mean
import allantools

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
        
        self.xResult = []
        # make list of taus to calculate for:
        for K in range(1, maxK):        
            self.xResult.append(K * tau0Seconds)
        
        # non-overlapping ADEV using allantools 'freq' mode.
        # https://github.com/aewallin/allantools
        (self.xResult, adev, aderr, adn) = allantools.adev(dataSeries, 1 / tau0Seconds, data_type = "freq", taus = self.xResult)
        
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
    