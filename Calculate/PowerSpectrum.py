'''
Use the Discrete Fourier Transform functions from numpy.fft; Specifically the rfft(a[, n, axis, norm]) 
'''
import numpy as np

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
        
    def calculate(self, dataSeries, tau0Seconds):
        n = len(dataSeries)
        fSampling = 1 / tau0Seconds
        # real FFT, normalized amplitude:
        fourierTransform = np.fft.rfft(dataSeries) / n
        # make array of bin numbers:
        binNums = np.arange(int(n / 2))
        # scale bin numbers to frequencies: 
        frequencies = binNums * fSampling / n 
        # return frequencies as xResult:
        self.xResult = frequencies.tolist();
        # return amplitude spectral density as yResult:
        self.yResult = abs(fourierTransform).tolist()
        return True
