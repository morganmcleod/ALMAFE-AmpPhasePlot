import Database.Driver.SQLite as driver
import Database.TagsDatabase as TagsDB
from Utility import ParseTimeStamp
from datetime import timedelta
from itertools import zip_longest

class TimeSeriesHeader(object):
    def __init__(self, timeSeriesId, startTime, tau0Seconds):
        self.timeSeriesId = timeSeriesId
        self.startTime = startTime
        self.tau0Seconds = tau0Seconds
    
class TimeSeries(object):
    def __init__(self, dataSeries, timeStamps, temperatures1, temperatures2):
        self.dataSeries = dataSeries
        self.timeStamps = timeStamps
        self.temperatures1 = temperatures1
        self.temperatures2 = temperatures2

class TimeSeriesDatabase(object):
    '''
    Helper class for storing and loading time series in the local database.
    '''

    def __init__(self, localDatabaseFile):
        '''
        Constructor
        :param localDatabaseFile: Filename of local database.
        '''
        self.CHUNK_SIZE = 1000 # max records to load at a time
        connectionInfo = { 'localDatabaseFile' : localDatabaseFile }
        self.db = driver.DriverSQLite(connectionInfo)
        self.createLocalDatabase()
        self.tagsDb = TagsDB.TagsDatabase(self.db)

    def createLocalDatabase(self):
        '''
        Create the local database tables if they do not already exist.
        '''
        # find or create TimeSeriesHeader table:
        self.db.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeriesHeader';")
        if not self.db.fetchone()[0]:
            self.db.execute("""CREATE TABLE TimeSeriesHeader (
                                keyId INTEGER PRIMARY KEY,
                                TS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                startTime TIMESTAMP,
                                tau0Seconds FLOAT);
                            """)
        
        # find or create TimeSeries table:
        self.db.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeries';")
        if not self.db.fetchone()[0]:
            self.db.execute("""CREATE TABLE TimeSeries (
                                fkHeader INTEGER, 
                                timeStamp TIMESTAMP,
                                seriesData FLOAT,
                                temperatures1 FLOAT,
                                temperatures2 FLOAT,
                                FOREIGN KEY (fkHeader) 
                                    REFERENCES TimeSeriesHeader(keyId)
                                    ON DELETE CASCADE
                                );
                            """)
            self.db.execute("""CREATE INDEX tsHeader ON TimeSeries (fkHeader);""")
                              
        self.db.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeriesTags';")
        if not self.db.fetchone()[0]:
            self.db.execute("""CREATE TABLE TimeSeriesTags (
                                fkHeader INTEGER,
                                tagName TEXT,
                                tagValue TEXT,
                                FOREIGN KEY (fkHeader) 
                                    REFERENCES TimeSeriesHeader(keyId)
                                    ON DELETE CASCADE
                                );
                            """)
            self.db.execute("""CREATE INDEX tagHeader ON TimeSeriesTags (fkHeader);""")    
        
        self.db.commit()
    
    def insertTimeSeriesHeader(self, startTime, tau0Seconds):
        '''
        Insert a time series header record and return its keyId
        :param startTime:   datetime start time of the measurement 
        :param tau0Seconds: float sampling interval of the measurement
        :return timeSeriesId: int keyId of the new header record.
        '''
        self.db.execute("INSERT INTO TimeSeriesHeader (startTime, tau0Seconds) VALUES ('{0}', {1});".format(startTime, str(tau0Seconds)))
        self.db.execute("SELECT last_insert_rowid()")
        timeSeriesId = self.db.fetchone()[0]
        self.db.commit()
        return timeSeriesId
    
    def updateTimeSeriesHeader(self, timeSeriesId, startTime, tau0Seconds):
        '''
        Update a time series header record and return its keyId
        :param timeSeriesId: of the header to update
        :param startTime:   datetime start time of the measurement 
        :param tau0Seconds: float sampling interval of the measurement
        :return timeSeriesId: int keyId of the updated header record.
        '''
        if not timeSeriesId:
            raise ValueError('Invalid timeSeriesId.')
        self.db.execute("UPDATE TimeSeriesHeader SET startTime = '{0}', tau0Seconds = {1} WHERE keyId = {2};".format(startTime, str(tau0Seconds), timeSeriesId))
        self.db.commit()
        return timeSeriesId
    
    def insertTimeSeries(self, timeSeriesId, dataSeries, startTime, tau0Seconds, timeStamps = None, temperatures1 = None, temperatures2 = None):
        '''
        Insert a time series associated with the last timeSeriesId returned by insertTimeSeriesHeader
        :param dataSeries:    list of floats.  The main data series
        :param startTime:     datetime of the first measurement.
        :param tau0Seconds:   measurement integration time/sampling interval
        :param timeStamps:    list of datetimes.  If not provided, they will be generated from starTime and tau0Seconds
        :param temperatures1: list of temperature sensor readings taken concurrent with the dataSeries
        :param temperatures2: 2nd list of temperature sensor readings 
        '''
        if not timeSeriesId:
            raise ValueError('Invalid timeSeriesId.')
        
        q0 = "INSERT INTO TimeSeries (fkHeader, timeStamp, seriesData, temperatures1, temperatures2) VALUES "
        
        if not timeStamps:
            timeStamps = []
        if not temperatures1:
            temperatures1 = []
        if not temperatures2:
            temperatures2 = []

        # timeDelta and timeCount are for generating timeStamps if not provided
        timeDelta = timedelta(seconds = tau0Seconds)
        timeCount = startTime
        firstTime = True
        error = False
        maxRec = 500
        recNum = 0        
        # loop on data arrays:
        for TS, data, temp1, temp2 in zip_longest(timeStamps, dataSeries, temperatures1, temperatures2):
            if firstTime:
                q = ""
                firstTime = False
            else:
                q += ","
            
            # append fkHeader:    
            q += "({0}".format(timeSeriesId) 
                
            # append timeStamp:
            if TS:
                q += ",'{0}'".format(TS.strftime(self.db.TIMESTAMP_FORMAT))
            else:
                q += ",'{0}'".format(timeCount.strftime(self.db.TIMESTAMP_FORMAT))
                timeCount += timeDelta
            
            # append seriesData:
            q += ",{0}".format(data)
            
            # append temperatures1:
            if temp1:
                q += ",{0}".format(temp1)
            else:
                q += ",NULL"
            
            # append temperatures2:
            if temp2:
                q += ",{0}".format(temp2)
            else:
                q += ",NULL"
                
            q += ")"
            recNum += 1

            # if maxRec reached, perform the insert:
            if recNum == maxRec:
                # insert statement invariant part is q0 and record chunk is q:
                if not self.db.execute(q0 + q + ";", commit = False):
                    error = True
                # reset record counter:
                recNum = 0
                # reset flag to suppress comma:
                firstTime = True
        
        # it's likely theres a partial chunk at the end.  Insert it:
        if recNum:
            if not self.db.execute(q0 + q + ";", commit = False):
                error = True
        
        # no error seen, commit the transaction:
        if not error:
            self.db.commit()
        else:
            self.db.rollback()

    def retrieveTimeSeriesHeader(self, timeSeriesId):
        '''
        Retrieve the specified header row.
        :param timeSeriesId: keyId of header to fetch
        :return TimeSeriesHeader object if successful, None otherwise.
        '''
        if not timeSeriesId:
            raise ValueError('Invalid timeSeriesId.')
        tsParser = ParseTimeStamp.ParseTimeStamp()
        self.db.execute("SELECT startTime, tau0Seconds FROM TimeSeriesHeader WHERE keyId = {0}".format(timeSeriesId))

        result = None
        row = self.db.fetchone()
        if row:
            result = TimeSeriesHeader(timeSeriesId, tsParser.parseTimeStamp(row[0]), float(row[1]))
        return result
    
    def retrieveTimeSeries(self, timeSeriesId):
        '''
        Retrieve the selected time series data
        :param timeSeriesId: keyId of the corresponding header record
        :return TimeSeries object if successful, else None
        '''
        if not timeSeriesId:
            raise ValueError('Invalid timeSeriesId.')
        
        dataSeries = []
        temperatures1 = []
        temperatures2 = []
        timeStamps = []
        
        #object for parsing the timeStamp column:
        tsParser = ParseTimeStamp.ParseTimeStamp()
        
        self.db.execute("SELECT timeStamp, seriesData, temperatures1, temperatures2 FROM TimeSeries WHERE fkHeader = '{0}'".format(timeSeriesId))
        
        records = self.db.fetchmany(self.CHUNK_SIZE)
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
            records = self.db.fetchmany(self.CHUNK_SIZE)
        if dataSeries:
            return TimeSeries(dataSeries, timeStamps, temperatures1, temperatures2)
        else:
            return None

    def deleteTimeSeries(self, timeSeriesId):
        '''
        Delete a time series header and all of its associated data and tags.
        Rows in TimeSeries and TimeSeriesTags tables are deleted by CASCADE.
        :param timeSeriesId:  int of the time series to update
        '''
        q = "DELETE FROM TimeSeriesHeader WHERE keyId = {0}".format(timeSeriesId)
        if not self.db.execute(q, commit = False):
            self.db.rollback()
            return
        self.db.commit()

    def setTags(self, timeSeriesId, tagDictionary):
        '''
        Set, update, or delete tags on the specified time series:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param timeSeriesId:  int of the time series to update
        :param tagDictionary: dictionary of tag names and values.
        '''
        if not timeSeriesId:
            raise ValueError('Invalid timeSeriesId.')
        self.tagsDb.setTags(timeSeriesId, 'TimeSeriesTags', 'fkHeader', tagDictionary)
        
    def getTags(self, timeSeriesId, tagNames):
        '''
        Retrieve tag values on the specified time series:
        :param timeSeriesId: integer id of the time series to query
        :param tagNames: list of strings
        :return dictionary of {tagName, tagValue} where tagValue is None if the tag was not found.  String otherwise.
        '''
        if not timeSeriesId:
            raise ValueError('Invalid timeSeriesId.')
        return self.tagsDb.getTags(timeSeriesId, 'TimeSeriesTags', 'fkHeader', tagNames)
