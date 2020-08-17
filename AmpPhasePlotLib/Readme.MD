# AmpPhasePlotLib

Stability analysis and plotting functions.
Uses TimeSeries data from the TimeSeriesAPI to produce original plots.
Also uses Plot/Trace data from the ResultAPI to reproduce previous plots.

## [PlotAPI](PlotAPI.py) module

### All methods take the same input parameters:
* *plotElements*: a dict of {PlotEl : str} which will be used to clarify or override automatically computed elements.
* *outputName*: an optional path and filename where the resulting .png file should be stored.
* *show*: if true, causes the plot to be displayed in the default renderer (browser window or notebook).

### All methods return True if successful and update PlotAPI Public Attributes:
* imageData = binary image data in .png format
* plotElementsFinal = plotElements input dict merged with additional PlotEl values computed automatically.

### Methods to produce a plot from raw [TimeSeries](AmpPhaseDataLib/Readme.MD) data:
Produce a time series plot for a single timeSeries:
* plotTimeSeries(timeSeriesId, plotElements = {}, outputName = None, show = False)  

Produce an amplitude spectrum or power spectrum plot for a single timeSeries:
* plotSpectrum(timeSeriesId, plotElements = {}, outputName = None, show = False)

Produce an normalized Allan Variance plot of amplitude stability:
* plotAmplitudeStability(timeSeriesIds, plotElements = {}, outputName = None, show = False)  
  - timeSeriesIds can be a single id or a list. Error bars are shown by default if it is a single id, hidden for a list.

Produce a 2-point Allan Standard Deviation plot of phase stability:
* plotPhaseStability(timeSeriesIds, plotElements = {}, outputName = None, show = False)  
  - timeSeriesIds can be a single id or a list. Error bars are shown by default if it is a single id, hidden for a list.
  - This is a plot specifically required by ALMA and is not the same as the standard ADEV(phase).  

### Method to re-create a plot using data from the [ResultAPI](AmpPhaseDataLib/Readme.MD):
* rePlot(plotId, plotElements = {}, outputName = None, show = False)
  - supported only for stability plots and powerSpectrum plots.  (It doesn't make sense to store the whole original TimeSeries again in the Results database.)
