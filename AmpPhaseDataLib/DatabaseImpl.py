import sqlite3
from .ParseTimeStamp import ParseTimeStamp
from datetime import datetime, timedelta
import itertools

class DatabaseImpl(object):
    '''
    classdocs
    '''

    def __init__(self, localDatabaseFile):
        '''
        Constructor
        '''
        self.localDatabaseFile = localDatabaseFile
        self.dataSeriesId = None
    
    def OpenOrCreateLocalDatabase(self):
        if not self.localDatabaseFile:
            raise ValueError('No local database filename configured.')
        conn = sqlite3.connect(self.localDatabaseFile)
        cursor = conn.cursor()
        # find or create TimeSeriesHeader table:
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeriesHeader';")
        if not cursor.fetchone()[0]:
            cursor.execute("""CREATE TABLE TimeSeriesHeader (
                                TS TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                startTime TIMESTAMP,
                                tau0Seconds FLOAT, 
                                description TEXT);
                            """)
        
        # find or create TimeSeries table:
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='TimeSeries';")
        if not cursor.fetchone()[0]:
            cursor.execute("""CREATE TABLE TimeSeries (
                                fkHeader INTEGER, 
                                timeStamp TIMESTAMP,
                                seriesData FLOAT,
                                temperatures1 FLOAT,
                                temperatures2 FLOAT);
                            """)
        conn.commit()
        conn.close() 
    
    def InsertTimeSeriesHeader(self, description, startTime, tau0Seconds):
        if not self.localDatabaseFile:
            raise ValueError('No local database filename configured.')
        conn = sqlite3.connect(self.localDatabaseFile)
        cursor = conn.cursor()
        
        if not description:
            description = ""
        
        cursor.execute("INSERT INTO TimeSeriesHeader (startTime, tau0Seconds, description) VALUES ('{0}', {1}, '{2}')".format(startTime, str(tau0Seconds), description))
        cursor.execute("SELECT last_insert_rowid()")
        self.dataSeriesId = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return self.dataSeriesId
    
    def InsertTimeSeries(self, dataSeries, startTime, tau0Seconds, timeStamps = None, temperatures1 = None, temperatures2 = None):
        if not self.localDatabaseFile:
            raise ValueError('No local database filename configured.')
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
                q += ", '{0}'".format(TS.strftime('%Y-%m-%d %H:%M:%S.%f'))
            else:
                q += ", '{0}'".format(timeCount.strftime('%Y-%m-%d %H:%M:%S.%f'))
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
        
        conn = sqlite3.connect(self.localDatabaseFile)
        cursor = conn.cursor()
        cursor.execute(q)
        conn.commit()
        conn.close()

    def RetrieveTimeSeriesHeader(self, dataSeriesId):
        '''
        Retrieve the specified header row.
        If successful, populates self with 
        :param dataSeriesId: rowid of header to fetch
        :return (dataSeriesId, startTime, tau0Seconds, description) if successful, None otherwise.
        '''
        if not self.localDatabaseFile:
            raise ValueError('No local database filename configured.')
        if not dataSeriesId:
            raise ValueError('Invalid dataSeriesId.')
        tsParser = ParseTimeStamp()
        self.dataSeriesId = None
        conn = sqlite3.connect(self.localDatabaseFile)
        cursor = conn.cursor()
        cursor.execute("SELECT startTime, tau0Seconds, description FROM TimeSeriesHeader WHERE rowid = {0}".format(dataSeriesId))

        result = None
        row = cursor.fetchone()
        if row:
            result = (dataSeriesId, tsParser.parseTimeStamp(row[0]), float(row[1]), row[2])
        conn.close()
        return result
    
    def RetrieveTimeSeries(self, dataSeriesId):
        '''
        Retrieve the selected time series data
        :param dataSeriesId:
        :return (dataSeries[], timeStamps[], temperatures1[], temperatures2[]) if successful, else None
        '''
        CHUNK_SIZE = 1000
        if not self.localDatabaseFile:
            raise ValueError('No local database filename configured.')
        if not dataSeriesId:
            raise ValueError('Invalid dataSeriesId.')
        dataSeries = []
        temperatures1 = []
        temperatures2 = []
        timeStamps = []
        tsParser = ParseTimeStamp()
        conn = sqlite3.connect(self.localDatabaseFile)
        cursor = conn.cursor()        
        cursor.execute("SELECT timeStamp, seriesData, temperatures1, temperatures2 FROM TimeSeries WHERE fkHeader = '{0}'".format(dataSeriesId))
        records = cursor.fetchmany(CHUNK_SIZE)
        firstTime = True
        while records:
            for TS, data, temp1, temp2 in records:
                if firstTime:
                    # parse the first TS string and cache the format string:
                    timeStamp = tsParser.parseTimeStamp(TS)
                    firstTime = False
                else:
                    # parse subsequent TS strings using the cached format:
                    timeStamp = tsParser.tryParseTimeStamp(TS, tsParser.lastTimeStampFormat)
                timeStamps.append(timeStamp)
                dataSeries.append(data)
                if temp1:
                    temperatures1.append(temp1)
                if temp2:
                    temperatures2.append(temp2)
            records = cursor.fetchmany(CHUNK_SIZE)
        cursor.close()
        if dataSeries:
            return (dataSeries, timeStamps, temperatures1, temperatures2)
        else:
            return None