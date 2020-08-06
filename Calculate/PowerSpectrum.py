'''
Use the Discrete Fourier Transform functions from numpy.fft; Specifically the rfft(a[, n, axis, norm]) 
'''
import numpy as np
import bisect
from math import sqrt

class PowerSpectrum(object):
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
    
    def RMSfromFFT(self, bwLower, bwUpper, ASD = False):
        '''
        Calculate the RMS noise in the specified bandwidth using the FFT outputs from calculate() 
        Must be called after calculate()
        :param bwLower:
        :param bwUpper:
        '''
        iLower = bisect.bisect_left(self.xResult, bwLower)
        iUpper = bisect.bisect_right(self.xResult, bwUpper)
#         print("iLower={}, iUpper={}".format(iLower, iUpper))
#         print("xlower={}, xUpper={}".format(self.xResult[iLower], self.xResult[iUpper - 1]))
#         print("ylower={}, yUpper={}".format(self.yResult[iLower], self.yResult[iUpper - 1]))
        
        if ASD:
            # y is in V/rootHz.  y*y is V^2/Hz. binSize is Hz.  result is V
            sumSq = sum([y * y * self.binSize for y in self.yResult[iLower:iUpper]])
            return sqrt(sumSq)
        else: # PSD
            # y is in V^2/Hz. 
            tot = sum([(y * self.binSize) for y in self.yResult[iLower:iUpper]])
            return sqrt(tot)
        
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
        