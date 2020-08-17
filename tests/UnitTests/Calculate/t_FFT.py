from AmpPhaseDataLib.Constants import *
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
import numpy as np
from datetime import datetime

def makeFFTSamples():
    tsAPI = TimeSeriesAPI.TimeSeriesAPI()
    plotAPI = PlotAPI.PlotAPI()

    now = datetime.now()
    tsEls = {PlotEl.XUNITS : "ms", PlotEl.YRANGE_WINDOW : "-1, 1"}
    fftEls = {PlotEl.X_LINEAR : "1", PlotEl.Y_LINEAR : "1", PlotEl.YRANGE_WINDOW : "0, 1"}
    
    samples = 1000
    duration = 1  # seconds
    interval = duration / samples
    
    t = np.linspace(0, duration, samples)
 
    s = np.sin(40 * 2 * np.pi * t)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 Hz sin at amplitude 1")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "1 - 40.png")
    tsAPI.deleteTimeSeries(tsId)
 
    s = 0.5 * np.sin(40 * 2 * np.pi * t)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 Hz sin at amplitude 0.5")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "2 - 40 at 0.5.png")
    tsAPI.deleteTimeSeries(tsId)
 
    s = np.sin(40 * 2 * np.pi * t) ** 2
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 Hz sin^2 at amplitude 1")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "3 - sin^2.png")
    tsAPI.deleteTimeSeries(tsId)
 
    s = 0.5 * np.sin(40 * 2 * np.pi * t) ** 2
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 Hz sin^2 at amplitude 0.5")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "4 - sin^2 at 0.5.png")
    tsAPI.deleteTimeSeries(tsId)
    
    s = np.sin(40 * 2 * np.pi * t) + 0.5 * np.sin(90 * 2 * np.pi * t)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 Hz sin at amplitude 1 + 90 Hz at 0.5")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "5 - 40+90.png")
    tsAPI.deleteTimeSeries(tsId)
 
    s = 0.5 * np.sin(40 * 2 * np.pi * t) + 0.25 * np.sin(90 * 2 * np.pi * t)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 Hz sin at amplitude 0.5 + 90 Hz at 0.25")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "6 - 40+90 at 0.5.png")
    tsAPI.deleteTimeSeries(tsId)

    s = np.sin(40 * 2 * np.pi * t) + np.sin(43 * 2 * np.pi * t)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 + 43 Hz sin - resolvable in 1 Hz bins")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "7 - 40+43 resolvable.png")
    tsAPI.deleteTimeSeries(tsId)
    
    s = np.sin(40 * 2 * np.pi * t) + np.sin(40.5 * 2 * np.pi * t)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "40 + 40.5 Hz sin - unresolvable in 1 Hz bins")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), show = False)
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "8 - 40+40.5 unresolvable.png")
    tsAPI.deleteTimeSeries(tsId)
    
    s = np.random.normal(0, 1, size=samples)
    tsId = tsAPI.insertTimeSeries(s, tau0Seconds = interval, startTime = now)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, "normal(mean=0, stddev=1)")
    plotAPI.plotTimeSeries(tsId, dict(tsEls), outputName = "9 - normal noise.png")
    plotAPI.plotSpectrum(tsId, dict(fftEls), outputName = "9 - normal noise FFT.png")
    tsAPI.deleteTimeSeries(tsId)
