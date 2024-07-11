'''
Data management API for Amplitude and Phase stability Time Series
Exposes the following data model:

+------------------+
| TimeSeriesHeader |
| +timeSeriesId    |
| +tau0Seconds     |
| +startTime       |
| +tags            |
+------------------+
        | 1
        |
        |
        | 1
+------------------+
| TimeSeries       |
| +timeStamps[]    |
| +dataSeries[]    |
| +temperatures1[] |
| +temperatures2[] |
+------------------+

Where tags is a collection of name-value pairs, names given in Constants.py

TimeSeries and its metadata can be inserted all at once using insertTimeSeries()
Or it can be inserted in chunks or single values using startTimeSeries(), 
  insertTimeSeriesChunk(), finishTimeSeries()
'''

from AmpPhaseDataLib.Constants import DataSource, Units
from AmpPhaseDataLib.TimeSeries import TimeSeries
from Database.TimeSeriesDatabase import TimeSeriesDatabase
from typing import List, Optional, Union, Dict
from Utility import ParseTimeStamp
from datetime import datetime
import configparser

class TimeSeriesAPI(object):
    '''
    Data management API for Amplitude and Phase stability time series
    All parameters and returns values are Python builtins or enum, not implementation data structures.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # read database configuration:
        config = configparser.ConfigParser()
        config.read("AmpPhaseDataLib.ini")
        self.localDatabaseFile = config['Configuration']['localDatabaseFile']

        self.db = TimeSeriesDatabase(self.localDatabaseFile)
        self.tsParser = ParseTimeStamp.ParseTimeStamp()
    
    def startTimeSeries(self, 
            tau0Seconds:Optional[float] = None, 
            startTime:Optional[Union[str, datetime]] = None,
            dataUnits:Optional[Union[str, Units]] = Units.AMPLITUDE) -> TimeSeries:
        '''
        Create the TimeSeriesHeader and prepare to start inserting data points
        :param tau0Seconds:   float: integration time of each reading
        :param startTime:     datetime or str: when the measurement started
        :param dataUnits:     from Constans.Units enum.
        :return: timeSeries if successful, otherwise None
        '''
        timeSeries = TimeSeries(
            tsId = 0, 
            tau0Seconds = tau0Seconds, 
            startTime = startTime, 
            dataUnits = dataUnits
        )

        # create a time series header record and return the timeSeriesId:
        timeSeries.tsId = self.db.insertTimeSeriesHeader(timeSeries.startTime, tau0Seconds)
        if timeSeries.tsId:
            self.setDataSource(timeSeries.tsId, DataSource.UNITS, dataUnits.value)
            return timeSeries
        else:
            return None

    def finishTimeSeries(self, timeSeries:TimeSeries):
        '''
        Write out the time series data to the database.
        This may be called repeatedly in a measurement loop, like a 'flush' function, or once at the end.
        :param timeSeriesId: of the time series being written.  Pass the value that was returned by startTimeSeries().
        '''
        # fix up startTime, if not already provided:
        timeSeries.updateStartTime()
        # calculate tau0Seconds from timeStamps, if not already provided:
        timeSeries.initializeTau0Seconds()
        # check for validity:
        valid, msg = timeSeries.isValid()
        if not valid:
            raise ValueError(msg)
        # update the header in case startTime or tau0Seconds changed:
        self.db.updateTimeSeriesHeader(timeSeries.tsId, timeSeries.startTime, timeSeries.tau0Seconds)
        # get the data arrays and insert into database:
        self.db.insertTimeSeries(timeSeries.getDataForWrite())
    
    def insertTimeSeries(self, 
                         dataSeries:Union[float, List[float]], 
                         temperatures1:Optional[Union[float, List[float]]] = None,
                         temperatures2:Optional[Union[float, List[float]]] = None,
                         timeStamps:Optional[Union[str, List[str]]] = None,
                         tau0Seconds:Optional[float] = None, 
                         startTime:Optional[str] = None,
                         dataUnits:Optional[Units] = Units.AMPLITUDE):
        '''
        Insert a complete time series.
        :param dataSeries:    list of floats: the main data series to store   
        :param temperatures1: list of floats: temperature sensor measurements taken at the same time as dataSeries
        :param temperatures2: list of floats: temperature sensor measurements taken at the same time as dataSeries
        :param timeStamps:    list of dateTime strings corresponding to the points in dataSeries
                              several formats supported, YYYY/MM/DD HH:MM:SS.mmm preferred
        :param tau0Seconds:   float: integration time of each reading
        :param startTime:     dateTime string of first point in dataSeries
        :return:              integer timeSeriesId if successful.
        :raise ValueError:    if any data series is not at least two points.
        Either timeStamps or tau0seconds must be provided.
        If timeStamps is provided, startTime will be set to the first value, else now() if not provided. 
        '''
        timeSeries = self.startTimeSeries(tau0Seconds, startTime, dataUnits)
        timeSeries.appendData(dataSeries, temperatures1, temperatures2, timeStamps)
        self.finishTimeSeries(timeSeries)
        return timeSeries.tsId
    
    def retrieveTimeSeries(self, timeSeriesId):
        '''
        :param timeSeriesId: of time series to retrieve
        :return timeSeries if successful, otherwise None
        '''
        header = self.db.retrieveTimeSeriesHeader(timeSeriesId)
        if not header:
            return None

        dataUnits = self.getDataSource(timeSeriesId, DataSource.UNITS, Units.AMPLITUDE)
        timeSeries = TimeSeries(
            tsId = header.timeSeriesId, 
            tau0Seconds = header.tau0Seconds, 
            startTime = header.startTime,
            dataUnits = dataUnits
        )
        
        result = self.db.retrieveTimeSeries(timeSeries.tsId)
        if not result:
            # header was found but no   Ok.
            return timeSeries
            
        timeSeries.timeStamps = result.timeStamps
        timeSeries.dataSeries = result.dataSeries
        timeSeries.temperatures1 = result.temperatures1
        timeSeries.temperatures2 = result.temperatures2
        timeSeries.clearDirty()
        return timeSeries
            
    def deleteTimeSeries(self, timeSeriesId):
        '''
        :param timeSeriesId: of time series to delete
        '''
        self.db.deleteTimeSeries(timeSeriesId)
    
    def setDataSource(self, timeSeriesId:int, dataSource:Union[str, DataSource], value):
        '''
        Set a DataSource tag for a TimeSeries.
        :param timeSeriesId: int
        :param dataSource: str or DataSource enum from Constants.py        
        :param value:      str or None to delete
        '''
        if isinstance(dataSource, str):
            dataSource = DataSource.fromStr(dataSource)
        if not isinstance(dataSource, DataSource):
            raise TypeError('Use DataSource enum from Constants.py')
        self.db.setTags(timeSeriesId, { dataSource.value : value })
        
    def getDataSource(self, timeSeriesId, dataSource:Union[str, DataSource], default = None):
        '''
        Retrieve a DataSource tag for a TimeSeries
        :param timeSeriesId: int
        :param dataSource:   str or DataSource enum from Constants.py
        :param default:      value to return if not found
        '''
        if isinstance(dataSource, str):
            dataSource = DataSource.fromStr(dataSource)
        if not isinstance(dataSource, DataSource):
            raise TypeError('Use DataSource enum from Constants.py')
        if timeSeriesId == 0:
            return default
        result = self.db.getTags(timeSeriesId, [dataSource.value])
        return result.get(dataSource.value, default)
    
    def clearDataSource(self, timeSeriesId, dataSource:Union[str, DataSource]):
        '''
        Remove a DataSource tag for a TimeSeries
        :param timeSeriesId: int
        :param dataSource:   str or DataSource enum from Constants.py
        '''
        self.setDataSource(timeSeriesId, dataSource, None)
    
    def getAllDataSource(self, timeSeriesId: int) -> Dict[DataSource, str]:
        '''
        Get all DataSource tags for a TimeSeries
        :param timeSeriesId: int
        :return dict of {DataSource : str}
        '''
        retrieved = self.db.getTags(timeSeriesId, [el.value for el in DataSource])
        result = {}
        # replace key str values with DataSource enum values:
        for tag, value in retrieved.items():
            result[DataSource(tag)] = value
        return result
       
