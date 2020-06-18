import Database.Driver.SQLite as driver
from Utility import ParseTimeStamp
from datetime import timedelta
import itertools

class TimeSeriesDatabase(object):
    '''
    Helper class for storing and loading time series in the local database.
    '''

    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, localDatabaseFile):
        '''
        Constructor
        :param localDatabaseFile: Filename of local database.
        '''
        self.dataSeriesId = None
        self.CHUNK_SIZE = 1000 # max records to load at a time
        connectionInfo = { 'localDatabaseFile' : localDatabaseFile }
        self.DB = driver.DriverSQLite(connectionInfo)
        self.createLocalDatabase()
    
    def createLocalDatabase(self):
        '''
        Create the local database tables if they do not already exist.
        '''
        # find or create TimeSeriesHeader table:
        self.DB.query("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeriesHeader';")
        if not self.DB.fetchone()[0]:
            self.DB.query("""CREATE TABLE TimeSeriesHeader (
                                TS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                startTime TIMESTAMP,
                                tau0Seconds FLOAT, 
                                description TEXT);
                            """)
        
        # find or create TimeSeries table:
        self.DB.query("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeries';")
        if not self.DB.fetchone()[0]:
            self.DB.query("""CREATE TABLE TimeSeries (
                                fkHeader INTEGER, 
                                timeStamp TIMESTAMP,
                                seriesData FLOAT,
                                temperatures1 FLOAT,
                                temperatures2 FLOAT);
                            """)
            self.DB.query("""CREATE INDEX tsHeader ON TimeSeries (fkHeader);""")
                              
        self.DB.query("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeriesTags';")
        if not self.DB.fetchone()[0]:
            self.DB.query("""CREATE TABLE TimeSeriesTags (
                                fkHeader INTEGER,
                                tagName TEXT,
                                tagValue TEXT);
                            """)
            self.DB.query("""CREATE INDEX tagHeader ON TimeSeriesTags (fkHeader);""")    
        
        self.DB.commit()
    
    def insertTimeSeriesHeader(self, description, startTime, tau0Seconds):
        '''
        Insert a time series header record and return its rowid
        :param description: String description of the measurement
        :param startTime:   datetime start time of the measurement 
        :param tau0Seconds: float sampling interval of the measurement
        :return self.dataSeriesId: int rowid of the new header record.
        '''
        
        if not description:
            description = ""
        
        self.DB.query("INSERT INTO TimeSeriesHeader (startTime, tau0Seconds, description) VALUES ('{0}', {1}, '{2}')".format(startTime, str(tau0Seconds), description))
        self.DB.query("SELECT last_insert_rowid()")
        self.dataSeriesId = self.DB.fetchone()[0]
        self.DB.commit()
        return self.dataSeriesId
    
    def insertTimeSeries(self, dataSeries, startTime, tau0Seconds, timeStamps = None, temperatures1 = None, temperatures2 = None):
        '''
        Insert a time series associated with the last dataSeriesId returned by insertTimeSeriesHeader
        :param dataSeries:    list of floats.  The main data series
        :param startTime:     datetime of the first measurement.
        :param tau0Seconds:   measurement integration time/sampling interval
        :param timeStamps:    list of datetimes.  If not provided, they will be generated from starTime and tau0Seconds
        :param temperatures1: list of temperature sensor readings taken concurrent with the dataSeries
        :param temperatures2: 2nd list of temperature sensor readings 
        '''
        if not self.dataSeriesId:
            raise ValueError('No currently selected dataSeriesId.')
        if not dataSeries:
            raise ValueError('dataSeries is required.')
        
        q = "INSERT INTO TimeSeries (fkHeader, timeStamp, seriesData, temperatures1, temperatures2) VALUES "
        
        if not timeStamps:
            timeStamps = []
        if not temperatures1:
            temperatures1 = []
        if not temperatures1:
            temperatures2 = []

        # timeDelta and timeCount are for generating timeStamps if not provided
        timeDelta = timedelta(seconds = tau0Seconds)
        timeCount = startTime
        firstTime = True
        
        for TS, data, temp1, temp2 in itertools.zip_longest(timeStamps, dataSeries, temperatures1, temperatures2):
            if firstTime:
                q += "("
                firstTime = False
            else:
                q += ", ("
                
            q += str(self.dataSeriesId) 
                
            if TS:
                q += ", '{0}'".format(TS.strftime(self.TIMESTAMP_FORMAT))
            else:
                q += ", '{0}'".format(timeCount.strftime(self.TIMESTAMP_FORMAT))
                timeCount += timeDelta
            
            q += ", {0}".format(str(data))
            
            if temp1:
                q += ", {0}".format(str(temp1))
            else:
                q += ", NULL"
            
            if temp2:
                q += ", {0}".format(str(temp2))
            else:
                q += ", NULL"
                
            q += ")"
        
        self.DB.query(q, commit = True)

    def retrieveTimeSeriesHeader(self, dataSeriesId):
        '''
        Retrieve the specified header row.
        If successful, populates self.dataSeriesId
        :param dataSeriesId: rowid of header to fetch
        :return (dataSeriesId, startTime, tau0Seconds, description) if successful, None otherwise.
        '''
        if not dataSeriesId:
            raise ValueError('Invalid dataSeriesId.')
        tsParser = ParseTimeStamp.ParseTimeStamp()
        self.dataSeriesId = None
        self.DB.query("SELECT startTime, tau0Seconds, description FROM TimeSeriesHeader WHERE rowid = {0}".format(dataSeriesId))

        result = None
        row = self.DB.fetchone()
        if row:
            result = (dataSeriesId, tsParser.parseTimeStamp(row[0]), float(row[1]), row[2])
        return result
    
    def retrieveTimeSeries(self, dataSeriesId):
        '''
        Retrieve the selected time series data
        :param dataSeriesId: rowid of the corresponding header record
        :return (dataSeries[], timeStamps[], temperatures1[], temperatures2[]) if successful, else None
        '''
        if not dataSeriesId:
            raise ValueError('Invalid dataSeriesId.')
        
        dataSeries = []
        temperatures1 = []
        temperatures2 = []
        timeStamps = []
        
        #object for parsing the timeStamp column:
        tsParser = ParseTimeStamp.ParseTimeStamp()
        
        self.DB.query("SELECT timeStamp, seriesData, temperatures1, temperatures2 FROM TimeSeries WHERE fkHeader = '{0}'".format(dataSeriesId))
        
        records = self.DB.fetchmany(self.CHUNK_SIZE)
        firstTime = True
        while records:
            for TS, data, temp1, temp2 in records:
                if firstTime:
                    # parse the first TS string and cache the format string:
                    timeStamp = tsParser.parseTimeStamp(TS)
                    firstTime = False
                else:
                    # parse subsequent TS strings using the cached format:
                    timeStamp = tsParser.parseTimeStampWithFormatString(TS, tsParser.lastTimeStampFormat)
                timeStamps.append(timeStamp)
                dataSeries.append(data)
                if temp1:
                    temperatures1.append(temp1)
                if temp2:
                    temperatures2.append(temp2)
            records = self.DB.fetchmany(self.CHUNK_SIZE)
        if dataSeries:
            return (dataSeries, timeStamps, temperatures1, temperatures2)
        else:
            return None

    def setTimeSeriesTags(self, dataSeriesId, tagDictionary):
        '''
        Set, update, or delete tags on the specified time series:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param dataSeriesId:  integer id of the time series to update
        :param tagDictionary: dictionary of tag names and values.
        '''
        if not dataSeriesId:
            raise ValueError('Invalid dataSeriesId.')
        
        deleteList = []
        insertList = []
        
        for key, value in tagDictionary.items():
            if key:
                deleteList.append(key)
                if not (value is None or value is False):
                    insertList.append((key, value))
        
        if deleteList:
            q = "DELETE FROM TimeSeriesTags WHERE fkHeader = {0} AND (".format(dataSeriesId)
            firstTime = True
            for key in deleteList:
                if firstTime:
                    firstTime = False
                else:
                    q += " OR "
                q += "tagName = '{0}'".format(str(key))
            q += ");"
            self.DB.query(q)
    
        if insertList:
            q = "INSERT INTO TimeSeriesTags (fkHeader, tagName, tagValue) VALUES ("
            firstTime = True
            for item in insertList:
                if firstTime:
                    firstTime = False
                else:
                    q += "), ("
                q += "{0}, '{1}', '{2}'".format(dataSeriesId, str(item[0]), str(item[1]))
            q += ");"
            self.DB.query(q)
        
        self.DB.commit()
        
        
    def getTimeSeriesTags(self, dataSeriesId, tagNames):
        '''
        Retrieve tag values on the specified time series:
        :param dataSeriesId: integer id of the time series to query
        :param tagNames: list of strings
        :return dictionary of {tagName, tagValue} where tagValue is None if the tag was not found.  String otherwise.
        '''
        if not dataSeriesId:
            raise ValueError('Invalid dataSeriesId.')
        
        q = "SELECT tagName, tagValue FROM TimeSeriesTags WHERE fkHeader = {0} AND (".format(dataSeriesId)
        
        result = {}
        firstTime = True
        for tagName in tagNames:
            result[tagName] = None
            if firstTime:
                firstTime = False
            else:
                q += " OR "
            q += "tagName = '{0}'".format(str(tagName))
        q += ");"
        
        self.DB.query(q)
        records = self.DB.fetchmany(self.CHUNK_SIZE)
        while records:
            for tagName, tagValue in records:
                result[tagName] = tagValue
            records = self.DB.fetchmany(self.CHUNK_SIZE)
            
        return result
