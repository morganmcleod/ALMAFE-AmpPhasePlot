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
        samplingFrequency = 1 / tau0Seconds
        tpCount = len(dataSeries)
        
        fourierTransform = np.fft.rfft(dataSeries) / tpCount          # Normalize amplitude
        values = np.arange(int(tpCount / 2))
        timePeriod = tpCount / samplingFrequency
        frequencies = values / timePeriod
        
        self.xResult = frequencies.tolist();
        self.yResult = abs(fourierTransform).tolist()
        return True
