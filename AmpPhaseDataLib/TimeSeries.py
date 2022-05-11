from AmpPhaseDataLib.Constants import Units
from Utility.ParseTimeStamp import ParseTimeStamp
from typing import List, Optional, Union
from datetime import datetime
from math import log10

class TimeSeries():
    
    def __init__(self, tsId:int = 0, tau0Seconds:float = None, startTime:Optional[Union[str, datetime]] = None):
        self.reset()
        self.tsId = tsId
        self.tau0Seconds = tau0Seconds
        self.initializeStartTime(startTime)
        
    def reset(self):
        # time series state data:
        self.tsId:int = 0
        self.dataSeries:List[float] = []
        self.temperatures1:List[float] = []
        self.temperatures2:List[float] = []
        self.timeStamps:List[datetime] = []
        self.tau0Seconds:float = None
        self.startTime:datetime = None
        # helper objects:
        self.nextWriteIndex:int = 0
        self.tsFormat:str = None
        self.tsParser:ParseTimeStamp = None
    
    def initializeStartTime(self, startTime:Optional[Union[str, datetime]] = None):
        '''
        Preserves self.startTime if already set.
        :param startTime: datetime or string of first point in dataSeries
        :return True if startTime was modified
        '''
        if not self.startTime:
            if isinstance(startTime, datetime):
                self.startTime = startTime
                return True
            elif isinstance(startTime, str):
                self.startTime = self.parseTimeStamp(startTime)
                return True
            else:
                return False
        return False
    
    def updateStartTime(self):
        '''
        Preserves self.startTime if already set. Else initialize it from timeStamps[0] or now()
        :return True if startTime was modified
        '''
        if not self.startTime:
            if len(self.timeStamps) > 0:
                self.startTime = self.timeStamps[0]
                return True
            else:
                self.startTime = datetime.now()
                return True
        return False
    
    def initializeTau0Seconds(self):
        '''
        Preserves tau0Seconds if already set, otherwise initialize from timeStamps
        :return True if tau0Seconds was modified
        '''
        if not self.tau0Seconds:
            if len(self.timeStamps) >= 2: 
                duration = (self.timeStamps[-1] - self.timeStamps[0]).total_seconds()
                self.tau0Seconds = duration / (len(self.timeStamps) - 1)
                return True
        return False

    def isValid(self):
        valid = True
        msg = ""
        if not self.tsId > 0:
            valid = False
            msg = "timeSeries.tsId must be a positive integer"
        elif len(self.dataSeries) < 2:
            valid = False
            msg = "dataSeries must contain at least 2 points"
        elif len(self.timeStamps) < 2 and self.tau0Seconds is None:
            valid = False
            msg = "you must provide either tau0Seconds or timeStamps list"
        return valid, msg
        
    def isDirty(self):
        '''
        :return True if some data in memory has not been written to the database.
        '''
        return self.nextWriteIndex < len(self.dataSeries)
    
    def clearDirty(self):
        '''
        Set internal state to indicate that all data in memory matches database.
        '''
        self.nextWriteIndex = len(self.dataSeries)
    
            
    def appendData(self, dataSeries:Union[float, List[float]], 
                         temperatures1:Optional[Union[float, List[float]]] = None,
                         temperatures2:Optional[Union[float, List[float]]] = None,
                         timeStamps:Optional[Union[str, List[str]]] = None):
        '''
        :param timeStamps: single or list of timeStamp corresponding to the points in dataSeries
                           several formats supported, YYYY/MM/DD HH:MM:SS.mmm preferred
        '''
        def appendOrConcat(target, itemOrList):
            if itemOrList is not None:
                try:
                    target += itemOrList
                except:
                    target.append(itemOrList)    
        
        appendOrConcat(self.dataSeries, dataSeries)
        appendOrConcat(self.temperatures1, temperatures1)
        appendOrConcat(self.temperatures2, temperatures2)

        if timeStamps:
            if isinstance(timeStamps, str):
                appendOrConcat(self.timeStamps, self.parseTimeStamp(timeStamps))
            elif isinstance(timeStamps, list):
                # it's a list of strings.
                appendOrConcat(self.timeStamps, [self.parseTimeStamp(ts) for ts in timeStamps])
            self.initializeStartTime(self.timeStamps[0])
    
    def getDataForWrite(self):
        ds = self.dataSeries[self.nextWriteIndex:] 
        ts = self.timeStamps[self.nextWriteIndex:] if self.timeStamps else []
        t1 = self.temperatures1[self.nextWriteIndex:] if self.temperatures1 else []
        t2 = self.temperatures2[self.nextWriteIndex:] if self.temperatures2 else []
        # Move the nextWriteIndex up so we don't write the same data again
        self.nextWriteIndex = len(self.dataSeries)
        return ds, ts, t1, t2
    
    def getDataSeries(self, currentUnits:Units, requiredUnits:Units = None):
        '''
        Get the dataSeries array, optionally converted to requiredUnits
        :param timeSeriesId
        :param requiredUnits: enum Units from Constants.py
        :return list derived from self.dataSeries converted, if possible
        '''
        if not requiredUnits or currentUnits == requiredUnits:
            # no coversion needed:
            return self.dataSeries
        
        result = None
        
        if currentUnits == Units.WATTS:
            if requiredUnits == Units.MW:
                # convert from watt to mW:
                result = [y * 1000 for y in self.dataSeries]
            
            if requiredUnits == Units.DBM:
                # convert from watt to dBm:
                result = [10 * log10(y * 1000) for y in self.dataSeries]
        
        elif currentUnits == Units.MW:
            if requiredUnits == Units.WATTS:
                # convert from mW to watt:
                result = [y / 1000 for y in self.dataSeries]
            
            if requiredUnits == Units.DBM:
                # convert from mW to dBm:
                result = [10 * log10(y) for y in self.dataSeries]
        
        elif currentUnits == Units.DBM:
            if requiredUnits == Units.WATTS:
                # convert from dBm to watt:
                result = [pow(10, y / 10) / 1000 for y in self.dataSeries]
            
            if requiredUnits == Units.MW:
                # convert from dBm to mW:
                result = [pow(10, y / 10) for y in self.dataSeries]
        
        elif currentUnits == Units.VOLTS:
            if requiredUnits == Units.MV:
                # convert from Volt to mV
                result = [y * 1000 for y in self.dataSeries]
        
        elif currentUnits == Units.MV:
            if requiredUnits == Units.VOLTS:
                # convert from mV to Volt
                result = [y / 1000 for y in self.dataSeries]
        else:
            # not supported:
            raise TypeError('Unsupported units conversion')
        
        return result

    def getTimeStamps(self, currentUnits:Units = Units.LOCALTIME, requiredUnits:Units = None):
        '''
        Get the timeStamps array, optionally converted to requiredUnits
        :param requiredUnits: enum Units from Constants.py
        :return list derived from self.dataSeries converted, if possible
        '''
        # only storing as LOCALTIME is supported for now:
        if currentUnits != Units.LOCALTIME:
            # not supported:
            raise TypeError('Unsupported units conversion')
        
        # timestamps are always stored as LOCALTIME:
        if not requiredUnits or requiredUnits == Units.LOCALTIME: 
            # no conversion:
            return self.timeStamps
        
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
            raise TypeError('Unsupported units conversion')
        
        return result  

    def parseTimeStamp(self, timeStamp:str):
        '''
        Implement loading a single timestamp, using cached timeStampFormat if available:
        :param timeStamp: single timeStamp string
        '''
        if not self.tsParser:
            self.tsParser = ParseTimeStamp()
        if self.tsFormat:
            # use the cached format string:
            return self.tsParser.parseTimeStampWithFormatString(timeStamp, self.tsFormat)
        else:
            # Call the full parser and store the format for next time
            timeStamp = self.tsParser.parseTimeStamp(timeStamp)
            self.tsFormat = self.tsParser.lastTimeStampFormat
            return timeStamp

    
        