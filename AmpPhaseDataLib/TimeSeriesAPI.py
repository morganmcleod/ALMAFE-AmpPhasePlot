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

from AmpPhaseDataLib.Constants import DataStatus, DataSource, Units
from AmpPhaseDataLib.TimeSeries import TimeSeries
from Database.TimeSeriesDatabase import TimeSeriesDatabase
from Database.TagsTools import applyDataStatusRules
from typing import List, Optional, Union
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
    
    def startTimeSeries(self, tau0Seconds:Optional[float] = None, startTime:Optional[Union[str, datetime]] = None):
        '''
        Create the TimeSeriesHeader and prepare to start inserting data points
        :param tau0Seconds:   float: integration time of each reading
        :param startTime:     datetime or str: when the measurement started
        :return: timeSeries if successful, otherwise None
        '''
        timeSeries = TimeSeries(0, tau0Seconds, startTime)
        # create a time series header record and return the timeSeriesId:
        timeSeries.tsId = self.db.insertTimeSeriesHeader(timeSeries.startTime, timeSeries.tau0Seconds)
        if timeSeries.tsId:
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
        ds, ts, t1, t2 = timeSeries.getDataForWrite()
        self.db.insertTimeSeries(timeSeries.tsId, ds, timeSeries.startTime, timeSeries.tau0Seconds, ts, t1, t2)
    
    def insertTimeSeries(self, 
                         dataSeries:Union[float, List[float]], 
                         temperatures1:Optional[Union[float, List[float]]] = None,
                         temperatures2:Optional[Union[float, List[float]]] = None,
                         timeStamps:Optional[Union[str, List[str]]] = None,
                         tau0Seconds:Optional[float] = None, 
                         startTime:Optional[str] = None):
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
        timeSeries = self.startTimeSeries(tau0Seconds, startTime)
        self.insertTimeSeriesChunk(timeSeries, dataSeries, temperatures1, temperatures2, timeStamps)
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
        timeSeries = TimeSeries(header.timeSeriesId, header.tau0Seconds, header.startTime)
        
        result = self.db.retrieveTimeSeries(timeSeries.tsId)
        if not result:
            # header was found but no data.  Ok.
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
    
    def setDataStatus(self, timeSeriesId, dataStatus):
        '''
        Set a DataStatus tag for a TimeSeries.
        :param timeSeriesId: int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise TypeError('Use DataStatus enum from Constants.py')
        
        self.db.setTags(timeSeriesId, applyDataStatusRules(dataStatus))
    
    def getDataStatus(self, timeSeriesId, dataStatus):
        '''
        Retrieve Data Status key having either true/false value.
        :param timeSeriesId: int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise TypeError('Use DataStatus enum from Constants.py')
        result = self.db.getTags(timeSeriesId, [dataStatus.value])
        return dataStatus.value in result.keys()
        
    def clearDataStatus(self, timeSeriesId, dataStatus):
        '''
        Clear a DataStatus tag for a TimeSeries.
        :param timeSeriesId:   int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise TypeError('Use DataStatus enum from Constants.py')
        self.db.setTags(timeSeriesId, { dataStatus.value : None })
    
    def getAllDataStatus(self, timeSeriesId):
        '''
        Get all DataStatus tags for a timeSeries:
        :param timeSeriesId: int
        :return dict of {DataStatus : str}
        '''
        retrieved = self.db.getTags(timeSeriesId, [el.value for el in DataStatus])
        result = {}
        # replace key str values with DataStatus enum values:
        for tag, value in retrieved.items():
            result[DataStatus(tag)] = value
        return result
    
    def setDataSource(self, timeSeriesId, dataSource, value):
        '''
        Set a DataSource tag for a TimeSeries.
        :param timeSeriesId: int
        :param dataSource: DataSource enum from Constants.py        
        :param value:      str or None to delete
        '''
        if not isinstance(dataSource, DataSource):
            raise TypeError('Use DataSource enum from Constants.py')
        self.db.setTags(timeSeriesId, { dataSource.value : value })
        
    def getDataSource(self, timeSeriesId, dataSource, default = None):
        '''
        Retrieve a DataSource tag for a TimeSeries
        :param timeSeriesId: int
        :param dataSource:   DataSource enum from Constants.py
        :param default:      value to return if not found
        '''
        if not isinstance(dataSource, DataSource):
            raise TypeError('Use DataSource enum from Constants.py')
        result = self.db.getTags(timeSeriesId, [dataSource.value])
        return result.get(dataSource.value, default)
    
    def clearDataSource(self, timeSeriesId, dataSource):
        '''
        Remove a DataSource tag for a TimeSeries
        :param timeSeriesId: int
        :param dataSource:   DataSource enum from Constants.py
        '''
        self.setDataSource(timeSeriesId, dataSource, None)
    
    def getAllDataSource(self, timeSeriesId):
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
       
