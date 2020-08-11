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
from Database import TimeSeriesDatabase
from Database.TagsTools import applyDataStatusRules
from Utility import ParseTimeStamp
from datetime import datetime
from math import log10, sqrt
import configparser

# TODO: define our own exceptions instead of using ValueError

class TimeSeriesAPI(object):
    '''
    Data management API for Amplitude and Phase stability time series
    All parameters and returns values are Python builtins or enum, not implementation data structures.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__reset()
        self.__loadConfiguration()
        self.db = TimeSeriesDatabase.TimeSeriesDatabase(self.localDatabaseFile)
        self.tsParser = ParseTimeStamp.ParseTimeStamp()
    
    def startTimeSeries(self, tau0Seconds = None, startTime = None):
        '''
        Create the TimeSeriesHeader and prepare to start inserting data points
        :param tau0Seconds:   float: integration time of each reading
        :param startTime:     dateTime str when the measurement started
        :return: timeSeriesId int if successful, otherwise None
        if tau0Seconds is not provided, then subsequent data inserts must include timeStamps.
        '''
        self.dataSeries = []
        self.temperatures1 = []
        self.temperatures2 = []
        self.timeStamps = []
        self.tau0Seconds = tau0Seconds
        self.__initializeStartTime(startTime)
        self.timeSeriesId = None
        # create a time series header record and return the timeSeriesId:
        self.timeSeriesId = self.db.insertTimeSeriesHeader(self.startTime, self.tau0Seconds)
        return self.timeSeriesId
    
    def insertTimeSeriesChunk(self, dataSeries, temperatures1 = None, temperatures2 = None, timeStamps = None):
        '''
        Insert one or more points of a dataSeries, using the last timeSeriesId allocated by startTimeSeries.
        :param dataSeries:    single or list of floats: chunk of the main data series to store
        :param temperatures1: single or list of floats: chunk of temperature sensor measurements
        :param temperatures2: single or list of floats: chunk of temperature sensor measurements
        :param timeStamps:    single or list of dateTime strings corresponding to the points in dataSeries
                              several formats supported, YYYY/MM/DD HH:MM:SS.mmm preferred
        '''
        self.dataSeries.append(dataSeries)
        if temperatures1:
            self.temperatures1.append(temperatures1)
        if temperatures2:
            self.temperatures2.append(temperatures2)
        self.__loadTimeStamps(timeStamps)

    def finishTimeSeries(self):
        '''
        Write out the time series data to the database.
        This may be called repeatedly in a measurement loop, like a 'flush' function, or once at the end.
        '''
        self.__validateTimeSeries()
        self.__validateTimeStampsStartTime()
        self.__initializeTau0Seconds()
        self.db.insertTimeSeries(self.dataSeries, self.startTime, self.tau0Seconds, self.timeStamps, self.temperatures1, self.temperatures2)
        
    def insertTimeSeries(self, 
                         dataSeries, 
                         temperatures1 = None, 
                         temperatures2 = None, 
                         timeStamps = None, 
                         tau0Seconds = None, 
                         startTime = None):
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
        self.dataSeries = dataSeries
        self.temperatures1 = temperatures1
        self.temperatures2 = temperatures2
        self.tau0Seconds = tau0Seconds
        self.timeStamps = []
        self.startTime = None
        self.timeSeriesId = None
        
        self.__validateTimeSeries()
        self.__loadTimeStamps(timeStamps)
        self.__validateTimeStampsStartTime()
        self.__initializeStartTime(startTime)
        self.__initializeTau0Seconds()
        self.timeSeriesId = self.db.insertTimeSeriesHeader(self.startTime, self.tau0Seconds)
        self.db.insertTimeSeries(self.dataSeries, self.startTime, self.tau0Seconds, self.timeStamps, self.temperatures1, self.temperatures2)
        return self.timeSeriesId
    
    def retrieveTimeSeries(self, timeSeriesId):
        '''
        :param timeSeriesId: of time series to retrieve
        :return timeSeriesId if successful, otherwise None
        '''
        self.__reset()
        header = self.db.retrieveTimeSeriesHeader(timeSeriesId)
        if not header:
            return None
        self.timeSeriesId = header.timeSeriesId
        self.startTime = header.startTime
        self.tau0Seconds = header.tau0Seconds
        
        result = self.db.retrieveTimeSeries(self.timeSeriesId)
        if not result:
            return None
        self.timeStamps = result.timeStamps
        self.dataSeries = result.dataSeries
        self.temperatures1 = result.temperatures1
        self.temperatures2 = result.temperatures2
        return self.timeSeriesId

    def getDataSeries(self, requiredUnits = None, isPower = False):
        '''
        Get the dataSeries array, optionally converted to requiredUnits
        :param requiredUnits: enum Units from Constants.py
        :param isPower:  If true, take the square root of each item.  For values representing a power detector (typically W or V)
        :return list derived from self.dataSeries converted, if possible
        '''
        units = Units.fromStr(self.getDataSource(self.timeSeriesId, DataSource.UNITS, (Units.AMPLITUDE).value))

        if requiredUnits and not isinstance(requiredUnits, Units):
            raise ValueError('Use Units enum from Constants.py')

        if not requiredUnits or units == requiredUnits:
            # no coversion needed:
            if isPower:
                return [sqrt(abs(y)) for y in self.dataSeries]
            else:
                return self.dataSeries

        # helper to take the square root or not depending on 'isPower':
        sqrtMaybe = lambda y: sqrt(abs(y)) if isPower else y
            
        result = None
        
        if units == Units.WATTS:
            if requiredUnits == Units.MW:
                # convert from watt to mW:
                result = [sqrtMaybe(y * 1000) for y in self.dataSeries]
            
            if requiredUnits == Units.DBM:
                # convert from watt to dBm:
                result = [10 * log10(y * 1000) for y in self.dataSeries]
        
        elif units == Units.MW:
            if requiredUnits == Units.WATTS:
                # convert from mW to watt:
                result = [sqrtMaybe(y / 1000) for y in self.dataSeries]
            
            if requiredUnits == Units.DBM:
                # convert from mW to dBm:
                result = [10 * log10(y) for y in self.dataSeries]
        
        elif units == Units.DBM:
            if requiredUnits == Units.WATTS:
                # convert from dBm to watt:
                result = [sqrtMaybe(pow(10, y / 10) / 1000) for y in self.dataSeries]
            
            if requiredUnits == Units.MW:
                # convert from dBm to mW:
                result = [sqrtMaybe(pow(10, y / 10)) for y in self.dataSeries]
        
        elif units == Units.VOLTS:
            if requiredUnits == Units.MV:
                # convert from Volt to mV
                result = [sqrtMaybe(y * 1000) for y in self.dataSeries]
        
        elif units == Units.MV:
            if requiredUnits == Units.VOLTS:
                # convert from mV to Volt
                result = [sqrtMaybe(y / 1000) for y in self.dataSeries]
        else:
            # not supported:
            raise ValueError('Unsupported units conversion')
        
        return result
    
    def getTimeStamps(self, requiredUnits = None):
        '''
        Get the timeStamps array, optionally converted to requiredUnits
        :param requiredUnits: enum Units from Constants.py
        :return list derived from self.dataSeries converted, if possible
        '''
        # timestamps are always stored as datetime:
        units = Units.LOCALTIME

        if not requiredUnits or units == requiredUnits: 
            # no conversion:
            return self.timeStamps
        
        if requiredUnits and not isinstance(requiredUnits, Units):
            raise ValueError('Use Units enum from Constants.py')
            
        if requiredUnits == Units.SECONDS or requiredUnits == Units.MINUTES: 
            # convert from datetime to seconds or minutes:
            div = 60 if requiredUnits == Units.MINUTES else 1  
            x0 = self.timeStamps[0]
            result = [(x - x0).seconds / div for x in self.timeStamps]
        elif requiredUnits == Units.MS:
            # convert from datetime to ms:
            x0 = self.timeStamps[0]
            result = [(x - x0).microseconds / 1000 for x in self.timeStamps]
        else:
            # not supported:
            raise ValueError('Unsupported units conversion')
        
        return result        
            
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
            raise ValueError('Use DataStatus enum from Constants.py')
        
        self.db.setTags(timeSeriesId, applyDataStatusRules(dataStatus))
    
    def getDataStatus(self, timeSeriesId, dataStatus):
        '''
        Retrieve Data Status key having either true/false value.
        :param timeSeriesId: int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise ValueError('Use DataStatus enum from Constants.py')
        result = self.db.getTags(timeSeriesId, [dataStatus.value])
        return dataStatus.value in result.keys()
        
    def clearDataStatus(self, timeSeriesId, dataStatus):
        '''
        Clear a DataStatus tag for a TimeSeries.
        :param timeSeriesId:   int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise ValueError('Use DataStatus enum from Constants.py')
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
            raise ValueError('Use DataSource enum from Constants.py')
        self.db.setTags(timeSeriesId, { dataSource.value : value })
        
    def getDataSource(self, timeSeriesId, dataSource, default = None):
        '''
        Retrieve a DataSource tag for a TimeSeries
        :param timeSeriesId: int
        :param dataSource:   DataSource enum from Constants.py
        :param default:      value to return if not found
        '''
        if not isinstance(dataSource, DataSource):
            raise ValueError('Use DataSource enum from Constants.py')
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
        
#// private implementation methods...
    
    def __reset(self):
        '''
        Initialize all data members to just-constructed state.
        Called in constructor and retrieveTimeSeries()  
        '''
        self.dataSeries = []
        self.temperatures1 = []
        self.temperatures2 = []
        self.timeStamps = []
        self.tau0Seconds = None
        self.startTime = None
        self.timeStampFormat = None
        self.timeSeriesId = None
    
    def __loadConfiguration(self):
        '''
        load our configuration file
        '''
        self.localDatabaseFile = None        
        config = configparser.ConfigParser()
        config.read("AmpPhaseDataLib.ini")
        self.localDatabaseFile = config['Configuration']['localDatabaseFile']
    
    def __validateTimeSeries(self):
        '''
        check for dataSeries minimum length
        '''
        dataLen = len(self.dataSeries)
        if dataLen < 2:
            raise ValueError('dataSeries must be a list of at least 2 points.')
        
    def __loadTimeStamps(self, timeStamps):
        '''
        :param timeStamps: single or list of timeStamp corresponding to the points in dataSeries
                           several formats supported, YYYY/MM/DD HH:MM:SS.mmm preferred
        '''
        if isinstance (timeStamps, str):
            self.__implLoadTimeStamp(timeStamps)
        elif isinstance(timeStamps, list):
            # it's a list of strings.  Iterate:
            for timeStamp in timeStamps:
                self.__implLoadTimeStamp(timeStamp)
    
    def __implLoadTimeStamp(self, timeStamp):
        '''
        Implement loading a single timestamp, using cached timeStampFormat if available:
        :param timeStamp: single timeStamp string
        '''
        if self.timeStampFormat:
            # use the cached format string:
            self.timeStamps.append(self.tsParser.parseTimeStampWithFormatString(timeStamp, self.timeStampFormat))
        else:
            # Call the full parser and store the format for next time
            self.timeStamps.append(self.tsParser.parseTimeStamp(timeStamp))
            self.timeStampFormat = self.tsParser.lastTimeStampFormat        
        
    def __validateTimeStampsStartTime(self):
        '''
        check for timeStamps or tao0Seconds provided, initialize startTime
        '''
        if isinstance(self.timeStamps, list):
            if len(self.timeStamps) > 0:
                if len(self.timeStamps) < 2:                
                    raise ValueError('timeStamps must be a list of at least 2 points.')
                if not self.startTime:
                    self.startTime = self.timeStamps[0]
        if not self.startTime and not self.tau0Seconds:
            raise ValueError('You must provide either timeStamps or tau0seconds.')
    
    def __initializeStartTime(self, startTime):
        '''
        :param startTime: dateTime string of first point in dataSeries
        '''
        if not self.startTime:
            if isinstance(startTime, str):
                self.startTime = self.tsParser.parseTimeStamp(startTime)
        if not self.startTime:
            self.startTime = datetime.now()
        
    def __initializeTau0Seconds(self):
        '''
        initialize tau0Seconds from timeStamps
        '''
        if not self.tau0Seconds:
            duration = (self.timeStamps[-1] - self.timeStamps[0]).total_seconds()
            self.tau0Seconds = duration / (len(self.timeStamps) - 1)

