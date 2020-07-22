# AmpPhasePlotLib

Stability analysis and plotting functions.
Uses TimeSeries data from the TimeSeriesAPI to produce original plots.
Also uses Plot/Trace data from the ResultAPI to reproduce previous plots.

## [PlotAPI](PlotAPI.py) module

### All PlotAPI methods take the same input parameters:

plotElements is a dict of {PlotEl : str} which will be used to clarify or override automatically computed elements.
See PlotEl and comments in Constants.py for details.

outputName is an optional path and filename where the .png file should be stored.

show causes the plot to be displayed in the default renderer (browser window or notebook).

### All methods return True if successful and update PlotAPI attributes:

imageData = binary image data in .png format

plotElementsFinal = plotElements input dict merged with additional PlotEl values computed automatically.


### plotTimeSeries(timeSeriesId, plotElements = {}, outputName = None, show = False)  
Produce a time series plot for a single timeSeries.

### plotPowerSpectrum(timeSeriesId, plotElements = {}, outputName = None, show = False)  
Produce a power spectrum plot for a single timeSeries.

### plotAmplitudeStability(timeSeriesIds, plotElements = {}, outputName = None, show = False)  
Produce an normalized Allan Variance plot of amplitude stability.  
timeSeriesIds can be a single id or a list.  
Error bars are shown by default if it is a single id and hidden otherwise.  

### plotPhaseStability(timeSeriesIds, plotElements = {}, outputName = None, show = False)  
Produce a 2-point Allan Standard Deviation plot of phase stability.  
This is a plot specifically required by ALMA and is not the same as the standard ADEV(phase).  
timeSeriesIds can be a single id or a list.  
Error bars are shown by default if it is a single id and hidden otherwise.  
