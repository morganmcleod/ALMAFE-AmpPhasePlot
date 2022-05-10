from AmpPhaseDataLib.Constants import DataSource, PlotEl
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
import os
import numpy as np

os.chdir('C:/BiasTestSet/ALMAFE-AmpPhasePlot')

tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

Fs = 1600.0
f = 250.0
samples = 100.0
x = np.linspace(0, samples / Fs, samples, endpoint = False)
y = np.sin(2 * np.pi * f * x) 


ts1 = tsa.insertTimeSeries(y, tau0Seconds = 1 / Fs)
tsa.setDataSource(ts1, DataSource.DATA_SOURCE, '250 Hz sin')
plotEls = {PlotEl.X_LINEAR : True,
           PlotEl.Y_LINEAR : True
           }
plt.plotTimeSeries(ts1, show = True)
plt.plotSpectrum(ts1, plotEls, show = True)
