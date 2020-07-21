# AmpPhaseDataLib

## Constants module
This module defines constants which are used in the following APIs.

## LegacyImport module
functions to import legacy TimeSeries data files.

## TimeSeriesAPI module
Data management API for Amplitude and Phase stability Time Series
Uses a fast, local SQLite database.

Exposes the following data model:

| TimeSeriesHeader |
| +timeSeriesId    |
| +tau0Seconds     |
| +startTime       |
| +tags            |
! 1
!
!
! 1
| TimeSeries       |
| +timeStamps[]    |
| +dataSeries[]    |
| +temperatures1[] |
| +temperatures2[] |

Where:
  tau0Seconds is the sampling interval/integration time of the dataSeries[]
  tags is a collection of name-value pairs, names given in Constants.py

* startTimeSeries(tau0Seconds = None, startTime = None)
Create a new TimeSeriesHeader and prepare to insert data.
Parameters are optional because these can often be derived from the dataSeries[]

* insertTimeSeriesChunk(dataSeries, temperatures1 = None, temperatures2 = None, timeStamps = None)
Insert single point or list of the data, say from a worker thread in the measurement app.
dataSeries is required.
timeStamps is required if tau0Seconds and startTime were not previously set.

* finishTimeSeries()
Finish adding to the last created TimeSeries.

* insertTimeSeries()
Insert a TimeSeries and its metadata all at once.
Equivalent to calling each of the above once in the order shown.

* retrieveTimeSeries(timeSeriesId)
Retrieve from the database by timeSeriesId

* getDataSeries(requiredUnits = None)
Fetch the dataSeries[] with optional Units conversion:
| Stored as | Fetch as        |
| WATTS     | MW              |
| WATTS     | DBM             |
| WATTS     | WATTS (no conv.)|
| VOLTS     | VOLTS (no conv.)|
| DEG       | DEG   (no conv.)|

* getTimeStamps(requiredUnits = None)
Fetch the timeStamps[] with optional Units conversion:
| Stored as | Fetch as|
| LOCALTIME | SECONDS|
| LOCALTIME | MINUTES|
| LOCALTIME | LOCALTIME (no conv.)|

* deleteTimeSeries(timeSeriesId)
Delete a TimeSeries and all associated data, by timeSeriesId

* DataStatus tag functions
DataStatus tags are boolean. Either present or absent.
Use DataStatus enums from Constants.py

setDataStatus(timeSeriesId, dataStatus)
getDataStatus(timeSeriesId, dataStatus)
clearDataStatus(timeSeriesId, dataStatus)
Set, Query, Delete a DataStatus tag.

getAllDataStatus(timeSeriesId)
returns dict of {DataStatus : str} where the str will be truthy, typically '1'.

* DataSource tag functions
DataSource tags have a str value
Use DataSource enums from Constants.py

setDataSource(timeSeriesId, dataSource, value)
getDataSource(timeSeriesId, dataSource)
clearDataSource(timeSeriesId, dataSource)

getAllDataSource(timeSeriesId)
returns dict of {DataSource : str}

## ResultsAPI module

Data management API for Amplitude and Phase stability Results
Uses a configured MySQL or compatible database server, 

Exposes the following data model:

| Result       |
| +resultId    |
| +description |
| +timeStamp   |
| +tags        |
!
!
! 0..*
| Plot   |       0..* | PlotImage  |
| +kind  |------------| +name      |
| +tags  |            | +path      |
!                     | +imageData |
!                     
!     
! 0..*
| Trace   |
| +name   |
| +legend | 
| +XYData |

Where:
  tags is a collection of name-value pairs, names given in Constants.py
  kind is enum defined in Constants.py
  imageData is binary and/or a image file on disk;
  XYData is float list of tuples (x, y, yError)

* Result object methods:
createResult(description, timeStamp = None)
retrieveResult(resultId)
updateResult(resultId, description = None, timeStamp = None)
deleteResult(resultId)
Also deletes all associated Plots, etc.

* DataStatus tag functions
DataStatus tags are boolean. Either present or absent.
Use DataStatus enums from Constants.py

setResultDataStatus(resultId, dataStatus)
getResultDataStatus(resultId, dataStatus)
clearResultDataStatus(resultId, dataStatus)
Set, Query, Delete a DataStatus tag.

* DataSource tag functions
DataSource tags have a str value
Use DataSource enums from Constants.py

setResultDataSource(resultId, dataSource, value)
getResultDataSource(resultId, dataSource)
clearResultDataSource(resultId, dataSource)

* Plot object methods:
All Plots must be referred to a Result object.

createPlot(resultId, kind)   # use PlotKind enum from Constants.py
retrievePlot(plotId)
deletePlot(plotId)
Also deletes all associated Traces and PlotImages.

* Plot element tags methods:
PlotEL tags have a str value.
Use PlotEl enum from Constants.py

setPlotEl(plotId, plotElement, value)
clearPlotEl(plotId, plotElement)
getPlotEl(plotId, plotElement)

* Plot Trace object methods:
All Traces must be referred to a Plot.

createTrace(plotId, xyData, name, legend = None)
retrieveTrace(traceId)
deleteTrace(traceId)

* PlotImage object methods:
All PlotImages must be referred to a Plot.

insertPlotImageFromFile(plotId, srcPath, name = None)
insertPlotImage(plotId, imageData, name = None)
retrievePlotImage(plotImageId)
retrievePlotImageToFile(plotImageId, targetPath)
deletePlotImage(plotImageId)

