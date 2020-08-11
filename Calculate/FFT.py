'''
Use the Fast Fourier Transform functions from numpy.fft 
'''
import numpy as np
import bisect
from math import sqrt

class FFT(object):
    '''
    Calculate power spectral density for a time series.
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
        self.binSize = None
        
    def calculate(self, dataSeries, tau0Seconds):
        '''
        calculate the real FFT of the dataSeries
        :param dataSeries:  list of float
        :param tau0Seconds: float sampling interval
        '''
        self.__reset()
        n = len(dataSeries)
        fSampling = 1 / tau0Seconds
        # real FFT, normalized amplitude:
        fourierTransform = np.fft.rfft(dataSeries) / n
        # correct for discarding half of two-sided spectrum:
        fourierTransform[1:] *= 2
        # make array of bin numbers:
        binNums = np.arange(len(fourierTransform))
        # scale bin numbers to frequencies:
        self.binSize = (fSampling / n)
        frequencies = binNums * self.binSize
        # return frequencies as xResult:
        self.xResult = frequencies.tolist();
        # return amplitude spectral density as yResult:
        self.yResult = abs(fourierTransform).tolist()
        return True
    
    def RMSfromFFT(self, bwLower = 0, bwUpper = 0):
        '''
        Calculate the RMS noise in the specified bandwidth using the FFT outputs from calculate() 
        Must be called after calculate()
        :param bwLower:
        :param bwUpper:
        '''
        iLower = bisect.bisect_left(self.xResult, bwLower) if bwLower else 0
        iUpper = bisect.bisect_right(self.xResult, bwUpper) if bwUpper else len(self.yResult)

#         print("iLower={}, iUpper={}, binSize={}".format(iLower, iUpper, self.binSize))
#         print("xlower={}, xUpper={}".format(self.xResult[iLower], self.xResult[iUpper - 1]))
#         print("ylower={}, yUpper={}".format(self.yResult[iLower], self.yResult[iUpper - 1]))
        
        f = lambda y, endPt: (y * (0.5 if endPt else 1) / sqrt(2)) ** 2
        
        sumSq = sum([f(y, False) for y in self.yResult[iLower + 1:iUpper - 1]] )
        sumSq += f(self.yResult[iLower], True) if (iLower > 0) else 0
        sumSq += f(self.yResult[iUpper-1], True)
        RMS = sqrt(sumSq) + self.yResult[0] if iLower == 0 else 0
        return RMS 
    
        
    def RMS(self, dataSeries, ASD = False):
        '''
        Utility function to calculate RMS from the given dataSeries
        :param dataSeries: list of float
        '''
        if ASD:
            variance = sum([y*y for y in dataSeries]) / len(dataSeries)
        else: # PSD
            variance = sum([y for y in dataSeries]) / len(dataSeries)
        return sqrt(variance)
        