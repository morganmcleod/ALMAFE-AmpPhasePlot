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

        self.reset()
        self.db = TimeSeriesDatabase(self.localDatabaseFile)
        self.tsParser = ParseTimeStamp.ParseTimeStamp()
    
    def reset(self):
        '''
        Initialize data members to just-constructed state.
        Called in constructor and retrieveTimeSeries()  
        '''
        self.timeSeries = TimeSeries()
    
    def startTimeSeries(self, tau0Seconds:Optional[float] = None, startTime:Optional[Union[str, datetime]] = None):
        '''
        Create the TimeSeriesHeader and prepare to start inserting data points
        :param tau0Seconds:   float: integration time of each reading
        :param startTime:     datetime or str: when the measurement started
        :return: timeSeriesId int if successful, otherwise None
        '''
        self.reset()
        self.timeSeries.tau0Seconds = tau0Seconds
        self.timeSeries.initializeStartTime(startTime)
        # create a time series header record and return the timeSeriesId:
        self.timeSeries.tsId = self.db.insertTimeSeriesHeader(self.timeSeries.startTime, self.timeSeries.tau0Seconds) 
        return self.timeSeries.tsId
    
    def insertTimeSeriesChunk(self, timeSeriesId:int,
                                    dataSeries:Union[float, List[float]], 
                                    temperatures1:Optional[Union[float, List[float]]] = None,
                                    temperatures2:Optional[Union[float, List[float]]] = None,
                                    timeStamps:Optional[Union[str, List[str]]] = None):
        '''
        Insert one or more points of a dataSeries, using the last timeSeriesId allocated by startTimeSeries.
        Handles timeSeriesId being different from previous API calls intelligently.
        
        :param timeSeriesId   of the time series being written.  Pass the value that was returned by startTimeSeries(). 
        :param dataSeries:    single or list of floats: chunk of the main data series to store
        :param temperatures1: single or list of floats: chunk of temperature sensor measurements
        :param temperatures2: single or list of floats: chunk of temperature sensor measurements
        :param timeStamps:    single or list of dateTime strings corresponding to the points in dataSeries
                              several formats supported, YYYY/MM/DD HH:MM:SS.mmm preferred
        '''
        self.__checkIdChanged(timeSeriesId)
        self.timeSeries.appendData(dataSeries, temperatures1, temperatures2, timeStamps)        

    def finishTimeSeries(self, timeSeriesId:int):
        '''
        Write out the time series data to the database.
        This may be called repeatedly in a measurement loop, like a 'flush' function, or once at the end.
        :param timeSeriesId: of the time series being written.  Pass the value that was returned by startTimeSeries().
        '''
        # check if timeSeriesId changed:
        self.__checkIdChanged(timeSeriesId)
        # fix up startTime, if not already provided:
        self.timeSeries.updateStartTime()
        # calculate tau0Seconds from timeStamps, if not already provided:
        self.timeSeries.initializeTau0Seconds()
        # check for validity:
        valid, msg = self.timeSeries.isValid()
        if not valid:
            raise ValueError(msg)
        # update the header in case startTime or tau0Seconds changed:
        self.db.updateTimeSeriesHeader(timeSeriesId, self.timeSeries.startTime, self.timeSeries.tau0Seconds)
        # get the data arrays and insert into database:
        ds, ts, t1, t2 = self.timeSeries.getDataForWrite()
        self.db.insertTimeSeries(timeSeriesId, ds, self.timeSeries.startTime, self.timeSeries.tau0Seconds, ts, t1, t2)
        
    def __checkIdChanged(self, timeSeriesId):
        if timeSeriesId != self.timeSeries.tsId:
            if self.timeSeries.isDirty():
                raise ValueError('New tsId is {} but previous tsId {} was not saved via finishTimeSeries(). Use reset() if you are sure.'
                                 .format(timeSeriesId, self.timeSeries.tsId))

            if not self.retrieveTimeSeries(timeSeriesId):
                raise ValueError('timeSeriesId {} is not a valid time series'.format(timeSeriesId))
    
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
        tsId = self.startTimeSeries(tau0Seconds, startTime)
        self.insertTimeSeriesChunk(tsId, dataSeries, temperatures1, temperatures2, timeStamps)
        self.finishTimeSeries(tsId)
        return tsId
    
    def retrieveTimeSeries(self, timeSeriesId):
        '''
        :param timeSeriesId: of time series to retrieve
        :return timeSeriesId if successful, otherwise None
        '''
        self.reset()
        header = self.db.retrieveTimeSeriesHeader(timeSeriesId)
        if not header:
            return None
        self.timeSeries.tsId = header.timeSeriesId
        self.timeSeries.startTime = header.startTime
        self.timeSeries.tau0Seconds = header.tau0Seconds
        
        result = self.db.retrieveTimeSeries(timeSeriesId)
        if not result:
            self.reset()
            return None
        self.timeSeries.timeStamps = result.timeStamps
        self.timeSeries.dataSeries = result.dataSeries
        self.timeSeries.temperatures1 = result.temperatures1
        self.timeSeries.temperatures2 = result.temperatures2
        self.timeSeries.clearDirty()
        return timeSeriesId

    @property
    def timeSeriesId(self):
        return self.timeSeries.tsId

    @property
    def startTime(self):
        return self.timeSeries.startTime
    
    @property
    def tau0Seconds(self):
        return self.timeSeries.tau0Seconds
    
    @property
    def temperatures1(self):
        return self.timeSeries.temperatures1

    @property
    def temperatures2(self):
        return self.timeSeries.temperatures1

    def getDataSeries(self, timeSeriesId:int, requiredUnits:Units = None):
        '''
        Get the dataSeries array, optionally converted to requiredUnits
        :param timeSeriesId
        :param requiredUnits: enum Units from Constants.py
        :return list derived from self.dataSeries converted, if possible
        '''
        self.__checkIdChanged(timeSeriesId)
        units = Units.fromStr(self.getDataSource(timeSeriesId, DataSource.UNITS, (Units.AMPLITUDE).value))

        if requiredUnits and not isinstance(requiredUnits, Units):
            raise TypeError('Use Units enum from Constants.py')
        return self.timeSeries.getDataSeries(units, requiredUnits)
    
    def getTimeStamps(self, requiredUnits:Units = None):
        '''
        Get the timeStamps array, optionally converted to requiredUnits
        :param requiredUnits: enum Units from Constants.py
        :return list derived from self.dataSeries converted, if possible
        '''
        if requiredUnits and not isinstance(requiredUnits, Units):
            raise TypeError('Use Units enum from Constants.py')
        return self.timeSeries.getTimeStamps(requiredUnits = requiredUnits)
            
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
       
