# AmpPhaseDataLib

## [Constants](Constants.py) module
This module defines constants which are used in the following APIs.

## [LegacyImport](LegacyImport.py) module
functions to import legacy TimeSeries data files.

## [TimeSeriesAPI](TimeSeriesAPI.py) module
Data management API for Amplitude and Phase stability Time Series
Uses a fast, local SQLite database.

Exposes the following data model:

#### *TimeSeriesHeader*
* +timeSeriesId
* +tau0Seconds
* +startTime
* +tags

#### *TimeSeries*
* +timeStamps[]
* +dataSeries[]
* +temperatures1[]
* +temperatures2[]

### Where:
* There is a 1-1 relationship between TimeSeriesHeader and TimeSeries.
* *tau0Seconds* is the sampling interval/integration time of the dataSeries[] and other arrays.
* *tags* is a collection of name-value pairs, names given in Constants.py.  Details below.

### Public Attributes:

These are updated by inserting data or by retriving from the database.

* dataSeries: 	 list of floats
* temperatures1: list of floats
* temperatures2: list of floats
* timeStamps:    list of datetime
* tau0Seconds:   float, integration interval in seconds
* timeSeriesId:  int

### startTimeSeries(tau0Seconds = None, startTime = None)

Create a new TimeSeriesHeader and prepare to insert data.
Parameters are optional because these can often be derived from the dataSeries[]

### insertTimeSeriesChunk(dataSeries, temperatures1 = None, temperatures2 = None, timeStamps = None)

Insert single point or list of the data, say from a worker thread in the measurement app.
dataSeries is required.
timeStamps is required if tau0Seconds and startTime were not previously set.

### finishTimeSeries()

Write out the time series data to the database.
This may be called repeatedly in a measurement loop, like a 'flush' function, or once at the end.

### insertTimeSeries(dataSeries, temperatures1 = None, temperatures2 = None, timeStamps = None, tau0Seconds = None, startTime = None)

Insert a TimeSeries and its metadata all at once.
Equivalent to calling each of the above three methods once in the order shown.

### retrieveTimeSeries(timeSeriesId)

Retrieve from the database by timeSeriesId.
Updates all Public Attributes, listed above.

### getDataSeries(requiredUnits = None)

Fetch the dataSeries[] with optional Units conversion:

* Amplitude data is stored as WATTS or VOLTS or unspecified AMPLITUDE.
  - If WATTS, it may be fetched as WATTS, MW, or DBM.
  - If VOLTS, it may be fetched as VOLTS, MV, or MICROVOLT.
  - If AMPLITUDE, or requiredUnits is None, it will be fetched without coversion.
* Phase data is stored as DEG.
  - It may only be fetched as DEG.

### getTimeStamps(requiredUnits = None)

Fetch the timeStamps[] with optional Units conversion:

* Time data is stored as LOCALTIME (YYYY-MM-DD HH:MM:SS.mmm).
  - It may be fetched as LOCALTIME, SECONDS, or MINUTES

### deleteTimeSeries(timeSeriesId)

Delete a TimeSeries and all associated data

### DataStatus tag functions

DataStatus tags describe the disposition of a Time Series.

DataStatus tags are boolean. Either present or absent. Use DataStatus enums from Constants.py.

Normally a Time Series will start out with DataStatus.UNKNOWN. If an error occurs or the test is stopped by the operator, use DataStatus.ERROR.  If it is determined whether the result meets specification, use DataStatus.MEET_SPEC or FAIL_SPEC.

DataStatus.TO_RETAIN and TO_DELETE are for data management after-the-fact of measurement.

Set, Query, Delete a DataStatus tag:
* setDataStatus(timeSeriesId, dataStatus)
* getDataStatus(timeSeriesId, dataStatus)
* clearDataStatus(timeSeriesId, dataStatus)  

Query multiple tags:
* getAllDataStatus(timeSeriesId)  
returns dict of {DataStatus : str} where the str will be truthy, typically '1'.

### DataSource tag functions

DataSource tags describe the configuration and other metadata at the time of measurement (or time of data creation for legacy data sets.)  They are used extensively in automatic plot labels.  Use as many as are applicable when inserting TimeSeries.

DataSource tags have a str value.  Use DataSource enums from Constants.py.

Set, Query, Delete a DataSource tag:
* setDataSource(timeSeriesId, dataSource, value)
* getDataSource(timeSeriesId, dataSource)
* clearDataSource(timeSeriesId, dataSource)

Query multiple tags:
* getAllDataSource(timeSeriesId)
returns dict of {DataSource : str}

DataSource tags:
* CONFIG_ID: of the device under test. This is usually an integer, but can be any uniquiely identifying string such as a SN.
* DATA_SOURCE: source data file on disk, if applicable.  Otherwise describe where this data came from.
* DATA_KIND: of the primary dataSeries. Values from DataKind enum:
  - "AMPLITUDE" unitless or unknown units. Treated as linear. 
  - "POWER"     typically W or dBm but could be V of a square-law detector
  - "PHASE"     linear degrees or radians
  - "VOLTAGE"   linear volts
* TEST_SYSTEM: name of measurement system or computer where the data was created
* UNITS: of the primary data series, like "dBm" or "deg".  Values from Units enum.
* T_UNITS: of the temperature data series, like "K".  Values from Units enum.
* LO_GHZ: the LO frequency in GHz
* RF_GHZ: typically for phase data, the RF in GHz
* TILT_ANGLE: tilt angle when measured.  applicable to FETMS amplitude and phase, mainly.
* SYSTEM: like "FE-20, Band 6"
* SUBSYSTEM: like "pol0, USB"
* SERIALNUM: of a serialized part under test
* OPERATOR: name or initials
* NOTES: operator notes at the time of measurement
* MEAS_SW_NAME: name of measurement software
* MEAS_SW_VERSION: version of measurement software

## [ResultAPI](ResultAPI.py) module

Data management API for Amplitude and Phase stability Results.

Uses a configured MySQL or compatible database server.

Exposes the following data model:

#### *Result*
* +resultId
* +description
* +timeStamp
* +tags

#### *Plot*
* +plotKind
* +tags

#### *PlotImage*
* +name
* +path
* +imageData

#### *Trace*
 * +name
 * +legend
 * +xyData

### Where:
* A Result can have zero or more Plots
* A Plot can have zero or more PlotImages
* A Plot can have zero or more Traces
* *tags* is a collection of name-value pairs, names given in Constants.py
* *plotKind* is enum PlotKind defined in Constants.py
* *imageData* is binary and/or a image file on disk
* *xyData* is a tuple of float lists ([x], [y], [yError]) with yError optional 

### Result object methods:
* createResult(description, timeStamp = None)
* retrieveResult(resultId)
* updateResult(resultId, description = None, timeStamp = None)
* deleteResult(resultId)
Also deletes all associated Plots, etc.

### DataStatus tag functions

DataStatus tags describe the disposition of a Result.

DataStatus tags are boolean. Either present or absent. Use DataStatus enums from Constants.py.

Normally a Result will start out with DataStatus.UNKNOWN. If an error occurs, use DataStatus.ERROR.  If it is determined whether the Result meets specification, use DataStatus.MEET_SPEC or FAIL_SPEC.

DataStatus.TO_RETAIN and TO_DELETE are for data management after-the-fact of measurement and analysis.

Set, Query, Delete DataStatus tag:
* setResultDataStatus(resultId, dataStatus)
* getResultDataStatus(resultId, dataStatus)
* clearResultDataStatus(resultId, dataStatus)  

### DataSource tag functions

DataSource tags describe the configuration and other metadata at the time of measurement (or time of data creation for legacy data sets.)  They are used extensively in automatic plot labels.  Use as many as are applicable when inserting TimeSeries.

DataSource tags have a str value.  Use DataSource enums from Constants.py.

Set, Query, Delete a DataSource tag:
* setResultDataSource(resultId, dataSource, value)
* getResultDataSource(resultId, dataSource)
* clearResultDataSource(resultId, dataSource)

The availble DataSource tags and their semantics are described above in the TimeSeriesAPI section.

### Plot object methods:

All Plots must be referred to a Result object.

* createPlot(resultId, plotKind)
Use PlotKind enum from Constants.py
* retrievePlot(plotId)
* deletePlot(plotId)
Also deletes all associated Traces and PlotImages.

### Plot element tags methods:

PlotEL tags have a str value. Use PlotEl enum from Constants.py.

The [PlotAPI](AmpPhasePlotLib/Readme.MD) methods populate several of these automatically.

Set, clear, get:
* setPlotEl(plotId, plotElement, value)
* clearPlotEl(plotId, plotElement)
* getPlotEl(plotId, plotElement)

Set all plot elements, removing any existing:
* setAllPlotEl(self, plotId, plotElements):

Get all plot elements as dict of {PlotEl : str}:
* def getAllPlotEl(self, plotId):

PlotEl Tags:
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
* RMS_SPEC: for AMPLITUDE_SPECTRUM plots, an RMS spec over a specified Hz bandwidth, like "fMin, fMax, specLimitRMS"
* SPEC_COMPLIANCE: string to add to plot indicating compliance
* FOOTER1: footer line 1
* FOOTER2: footer line 2 
* FOOTER3: footer line 3 
* IMG_WIDTH: pixels width of output image
* IMG_HEIGHT: pixels height of output image

### Plot Trace object methods:

All Traces must be referred to a Plot.
* createTrace(plotId, xyData, name, legend = None)
* retrieveTrace(traceId)
* retrieveTraces(plotId)
* deleteTrace(traceId)

### PlotImage object methods:

All PlotImages must be referred to a Plot.
* insertPlotImageFromFile(plotId, srcPath, name = None)
* insertPlotImage(plotId, imageData, name = None)
* retrievePlotImage(plotImageId)
* retrievePlotImageToFile(plotImageId, targetPath)
* deletePlotImage(plotImageId)
