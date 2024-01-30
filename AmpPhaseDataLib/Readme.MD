# AmpPhaseDataLib

## [Constants](Constants.py) module
This module defines constants which are used in the following APIs.

## [LegacyImport](LegacyImport.py) module
functions to import legacy TimeSeries data files.

## [TimeSeriesAPI](TimeSeriesAPI.py) module
Data management API for Amplitude and Phase stability Time Series.
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

```
    ts = startTimeSeries(tau0Seconds: Optional[float] = None, 
                         startTime: Optional[Union[str, datetime]] = None,
                         dataUnits: Optional[Union[str, Units]] = Units.AMPLITUDE):
```
Create a new TimeSeriesHeader and prepare to insert data.
Parameters are optional because these can often be derived from the dataSeries[]

Returns a TimeSeries object which you can subsequently add data to, either all at once or in variable size chunks
from, say from a worker thread in the measurement app.

```
    ts.appendData(dataSeries: Union[float, List[float]], 
                  temperatures1: Optional[Union[float, List[float]]] = None,
                  temperatures2: Optional[Union[float, List[float]]] = None,
                  timeStamps: Optional[Union[str, List[str]]] = None):
```
dataSeries is required.
temperatures1 and two are optional.
timeStamps is required if tau0Seconds and startTime were not previously set.
```
    finishTimeSeries(ts)
```
Write out the time series data to the database.
This may be called repeatedly in a measurement loop, like a 'flush' function, or once at the end.

```
    insertTimeSeries(dataSeries, temperatures1 = None, temperatures2 = None, timeStamps = None, tau0Seconds = None, startTime = None)
```
Insert a TimeSeries and its metadata all at once.
Equivalent to calling each of the above three methods once in the order shown.

```
    retrieveTimeSeries(timeSeriesId)
```
Retrieve from the database by timeSeriesId.
Updates all Public Attributes, listed above.

```
    getDataSeries(requiredUnits = None)
```
Fetch the dataSeries[] with optional Units conversion:

* Amplitude data is stored as WATTS or VOLTS or unspecified AMPLITUDE.
  - If WATTS, it may be fetched as WATTS, MW, or DBM.
  - If VOLTS, it may be fetched as VOLTS, MV, or MICROVOLT.
  - If AMPLITUDE, or requiredUnits is None, it will be fetched without coversion.
* Phase data is stored as DEG.
  - It may only be fetched as DEG.

```
    getTimeStamps(requiredUnits = None)
```
Fetch the timeStamps[] with optional Units conversion:

* Time data is stored as LOCALTIME (YYYY-MM-DD HH:MM:SS.mmm).
  - It may be fetched as LOCALTIME, SECONDS, or MINUTES


    deleteTimeSeries(timeSeriesId)

Delete a TimeSeries and all associated data

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
  - "amplitude" unitless or unknown units. Treated as linear. 
  - "power"     typically W or dBm but could be V of a square-law detector
  - "phase"     linear degrees or radians
  - "voltage"   linear volts
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

See [PlotAPI](AmpPhasePlotLib/Readme.MD) for descriptions of the PlotEls.

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
