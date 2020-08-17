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
        # correct for discarding half of two-sided spectrum - all bins but DC x2:
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
        
    def checkFFTSpec(self, minFreqHz, maxFreqHz, specLimit):
        '''
        Test whether the calculated spectrum is below a given spec line.
        Must be called after calculate()
        :param minFreqHz: lower frequency limit for the spec.
        :param maxFreqHz: upper frequency limit for the spec.  Must be >= minFreqHz.
        :param specLimit: maximum linear FFT value allowed in the range.
        :return True/False meets the spec
        '''
        # find the first and last bins to include in the calculation:
        iLower, iUpper = self.__findFreqRange(minFreqHz, maxFreqHz)
        
        for y in self.yResult[iLower:iUpper]:
            if y > specLimit:
                return False
        return True

    def RMSfromFFT(self, minFreqHz = 0, maxFreqHz = 0, includeDC = False):
        '''
        Calculate the RMS noise in the specified bandwidth using the FFT outputs from calculate() 
        Must be called after calculate()
        :param minFreqHz: Lowest frequency to include. If 0, may include the DC term.
        :param maxFreqHz: Highest frequency to include. If 0, include all frequencies. Must be >= minFreqHz.
        :param includeDC: If True, add the DC term to the RMS, otherwise dont include it even if minFreqHz == 0
        '''
        # find the first and last bins to include in the calculation:
        iLower, iUpper = self.__findFreqRange(minFreqHz, maxFreqHz)
        
        # we will sum the squares of the bins after converting each bin to RMS:
        #   bin / sqrt(2) : convert linear FTT to RMS
        #   RMS * 0.5 : for the two endPoint bins
        #   ** 2 : to take the sum of squares
        f = lambda y, endPoint: (y * (0.5 if endPoint else 1) / sqrt(2)) ** 2
        
        # sum the squares of all the non endPoint bins:
        sumSq = sum([f(y, False) for y in self.yResult[iLower + 1:iUpper - 1]] )
        # add in the lower endPoint bin if it is not the [0] DC bin:
        sumSq += f(self.yResult[iLower], True) if (iLower > 0) else 0
        # add in the upper endPoint bin:
        sumSq += f(self.yResult[iUpper-1], True)
        # take the sqrt to get the overall RMS:
        RMS = sqrt(sumSq)
        # If we want to include the DC bin, just add it in.  It has already been effectively /2 in calculate():
        if includeDC and iLower == 0:
            RMS += self.yResult[0]
        return RMS 
        
    def RMS(self, dataSeries):
        '''
        Testing utility function to calculate RMS from the given dataSeries.
        Does not use class data.
        Can be used to compare RMSfromFFT result to an RMS of the input time series.
        :param dataSeries: list of float
        '''
        variance = sum([y*y for y in dataSeries]) / len(dataSeries)
        return sqrt(variance)

    def __findFreqRange(self, minFreqHz = 0, maxFreqHz = 0):
        '''
        Private helper to find the indices corresponding to the provided frequency range.
        :param minFreqHz: lower frequency limit to find.  If 0, include the DC term.
        :param maxFreqHz: upper frequency limit for to find. If 0, include all frequencies. Must be >= minFreqHz.
        :return (iLower, iUpper): tuple of the first and last+1 indexes of self.xResult.
        '''
        iLower = bisect.bisect_left(self.xResult, minFreqHz) if minFreqHz else 0
        iUpper = bisect.bisect_right(self.xResult, maxFreqHz) if maxFreqHz else len(self.xResult)
        return (iLower, iUpper)
        