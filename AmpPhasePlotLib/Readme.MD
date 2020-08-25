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

### PlotEl Tags:
* XUNITS: of the primary x axis, like "seconds"
* YUNITS: of the primary y axis, like "dBm"
* Y2UNITS: of secondary y axis, like "K"
* ERROR_BARS: show error bars?  like "1" or "0"
* TITLE: plot title, overrides automatically generated
* X_AXIS_LABEL: overrides automatically generated from XUNITS
* Y_AXIS_LABEL: overrides automatically generated from YUNITS and/or DataSource.DATAKIND, and DataSource.UNITS
* Y2_AXIS_LABEL: overrides automatically generated from Y2UNITS and/or DataSource.T_UNITS
* Y2_LEGEND1: override legend for first temperature sensor trace.  Normally 'temperature sensor 1'
* Y2_LEGEND2: override legend for second temperature sensor trace.  Normally 'temperature sensor 2'
* XRANGE_PLOT; range of x values to plot, overriding auto defaults: 
  - value is a string like "float, float". Use for TMin, TMax for stability plots
* XRANGE_WINDOW: boundaries X-Y space to display.  String like "float, float"
* YRANGE_WINDOW: often needs to be larger than the data and spec lines so they are not at the edge.
* X_LINEAR: force the X axis to be linear when it would automatically be log, e.g. FFT plots
* Y_LINEAR: force the Y axis to be linear when it would normally be log, e.g. FFT plots
* SPEC_LINE1: list of two points to draw a spec line. Value is "x1, y1, x2, y2"
* SPEC_LINE2: list of two points to draw a second spec line. Value is "x1, y1, x2, y2"
* SPEC1_NAME: label for SPEC_LINE1
* SPEC2_NAME: label for SPEC_LINE2
* RMS_SPEC: for AMP_SPECTRUM plots, an RMS spec over a specified Hz bandwidth, like "fMin, fMax, specLimitRMS"
* SPEC_COMPLIANCE: string to add to plot indicating compliance
* SHOW_RMS: show the RMS of spectrum plots?  like "1" or "0"; default "0"
* FOOTER1: footer line 1
* FOOTER2: footer line 2 
* FOOTER3: footer line 3 
* IMG_WIDTH: pixels width of output image
* IMG_HEIGHT: pixels height of output image