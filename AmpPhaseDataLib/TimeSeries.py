from __future__ import annotations
from AmpPhaseDataLib.Constants import Units
from Calculate.Common import unwrapPhase
from Utility.ParseTimeStamp import ParseTimeStamp
from typing import List, Optional, Union, Tuple, Dict
from datetime import datetime
from math import log10
import numpy as np
from pydantic import BaseModel, validator
import copy

class TimeSeries(BaseModel):
    tsId: int = 0
    dataSeries: List[float] = []
    temperatures1: List[float] = []
    temperatures2: List[float] = []
    timeStamps: List[datetime] = []
    tau0Seconds: Optional[float] = None
    startTime: Optional[datetime | str] = None
    dataUnits: Optional[Units] = Units.AMPLITUDE
    nextWriteIndex: int = 0

    def reset(self):
        self.tsId = 0
        self.dataSeries = []
        self.temperatures1 = []
        self.temperatures2 = []
        self.timeStamps = []
        self.tau0Seconds = None
        self.startTime = None
        self.dataUnits = Units.AMPLITUDE
        self.nextWriteIndex = 0

    @validator('startTime')
    @classmethod
    def startTime_validator(cls, startTime):
        if not startTime:
            return None
        if isinstance(startTime, datetime):
            return startTime
        elif isinstance(startTime, str):
            return cls.parseTimeStamp(startTime)

    @validator('dataUnits')
    @classmethod
    def dataUnits_validator(cls, dataUnits):
        if isinstance(dataUnits, Units):
            return dataUnits
        if isinstance(dataUnits, str):
            return Units.fromStr(dataUnits)

    def __len__(self):
        return len(self.dataSeries)

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
            elif isinstance(timeStamps, datetime):
                self.timeStamps.append(timeStamps)
            elif isinstance(timeStamps, list):
                # it's a list of strings.
                appendOrConcat(self.timeStamps, [self.parseTimeStamp(ts) for ts in timeStamps])
            self.updateStartTime()

    def unwrapPhase(self, period = 2 * np.pi):
        self.dataSeries = unwrapPhase(self.dataSeries, period)

    def select(self,
            first: int = 0, 
            last: int = None,
            averaging: int = 1, 
            latestOnly: bool = False) -> TimeSeries:
        if latestOnly:
            return TimeSeries(
                tsId = self.tsId,
                dataSeries = [self.dataSeries[-1]] if self.dataSeries else [],
                temperatures1 = [self.temperatures1[-1]] if self.temperatures1 else [],
                temperatures2 = [self.temperatures2[-1]] if self.temperatures2 else [],
                timeStamps = [self.timeStamps[-1]] if self.timeStamps else [],
                tau0Seconds = self.tau0Seconds,
                startTime = self.startTime,
                dataUnits = self.dataUnits
            )
    
        else:
            if last is None:
                last = len(self.dataSeries)
            ts = TimeSeries(
                tsId = self.tsId,
                dataSeries = self.dataSeries[first:last] if self.dataSeries else [],
                temperatures1 = self.temperatures1[first:last] if self.temperatures1 else [],
                temperatures2 = self.temperatures2[first:last] if self.temperatures2 else [],
                timeStamps = self.timeStamps[first:last] if self.timeStamps else [],
                tau0Seconds = self.tau0Seconds,
                startTime = self.startTime,
                dataUnits = self.dataUnits
            )
            if averaging > 1:
                ts.dataSeries = (np.convolve(ts.dataSeries, np.ones(averaging), "valid") / averaging).tolist()
                if ts.tetemperatures1:
                    ts.temperatures1 = (np.convolve(ts.temperatures1, np.ones(averaging), "valid") / averaging).tolist()
                if ts.tetemperatures2:
                    ts.temperatures1 = (np.convolve(ts.temperatures1, np.ones(averaging), "valid") / averaging).tolist()
                if ts.timeStamps:
                    ts.timeStamps = ts.timeStamps[0:-1:averaging]
            return ts
    
    def getRecommendedAveraging(self, targetLength: int = 1000) -> int:
        if len(self.dataSeries) <= targetLength:
            return 1
        else:
            return len(self.dataSeries) // targetLength
    
    def getDataForWrite(self) -> TimeSeries:
        toWrite = self.select(self.nextWriteIndex)
        # Move the nextWriteIndex up so we don't write the same data again
        self.nextWriteIndex = len(self.dataSeries)
        return toWrite

    def getDataSeries(self, 
            requiredUnits:Optional[Union[str, Units]] = None,
            scale: Optional[float] = None,
            offset: Optional[float] = None,
            gainRef: Optional[float] = None):
        '''
        Get the dataSeries array, optionally converted to requiredUnits
        :param requiredUnits: enum Units from Constants.py or None
        :return list derived from self.dataSeries converted, if possible
        :raise TypeError if unsupported conversion requested
        '''
        if requiredUnits and isinstance(requiredUnits, str):
            requiredUnits = Units.fromStr(requiredUnits)
        
        if not requiredUnits or self.dataUnits == requiredUnits:
            # no conversion needed:
            return self.dataSeries
        
        result = copy.copy(self.dataSeries)

        if scale is not None:
            if offset is None:
                offset = 0
            result = [y * scale + offset for y in result]
        
        if self.dataUnits == Units.WATTS:
            if requiredUnits == Units.MW:
                # convert from watt to mW:
                result = [y * 1000 for y in result]
            
            if requiredUnits == Units.DBM:
                # convert from watt to dBm:
                result = [10 * log10(y * 1000) for y in result]
        
        elif self.dataUnits == Units.MW:
            if requiredUnits == Units.WATTS:
                # convert from mW to watt:
                result = [y / 1000 for y in result]
            
            if requiredUnits == Units.DBM:
                # convert from mW to dBm:
                result = [10 * log10(y) for y in result]
        
        elif self.dataUnits == Units.DBM:
            if requiredUnits == Units.WATTS:
                # convert from dBm to watt:
                result = [pow(10, y / 10) / 1000 for y in result]
            
            if requiredUnits == Units.MW:
                # convert from dBm to mW:
                result = [pow(10, y / 10) for y in result]

        elif self.dataUnits == Units.VOLTS:
            if requiredUnits == Units.MV:
                # convert from Volt to mV
                result = [y * 1000 for y in result]
            if requiredUnits == Units.DELTA_GAIN and gainRef is not None:
                result = [y / gainRef for y in result]

        elif self.dataUnits == Units.MV:
            if requiredUnits == Units.VOLTS:
                # convert from mV to Volt
                result = [y / 1000 for y in self.dataSeries]        
        else:
            # not supported:
            raise TypeError('Unsupported units conversion from {} to {}'.format(self.dataUnits.value, requiredUnits.value))
        
        return result

    def getTimeStamps(self, requiredUnits:Optional[Union[str, Units]] = None):
        '''
        Get the timeStamps array, optionally converted to requiredUnits
        :param requiredUnits: enum Units from Constants.py
        :return list derived from self.dataSeries converted, if possible
        '''
        if requiredUnits and isinstance(requiredUnits, str):
            requiredUnits = Units.fromStr(requiredUnits)
            
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
            raise TypeError('Unsupported units conversion from {} to {}'.format(Units.LOCALTIME.value, requiredUnits.value))
        
        return result  
    
    @classmethod
    def parseTimeStamp(cls, timeStamp:str):
        '''
        Implement loading a single timestamp, using cached timeStampFormat if available:
        :param timeStamp: single timeStamp string
        '''
        # static objects owned by this function:
        try:
            cls.tsParser
        except:
            cls.tsParser = ParseTimeStamp()
        
        try:
            cls.tsFormat
        except:
            cls.tsFormat = None

        if cls.tsFormat:
            # use the cached format string:
            return cls.tsParser.parseTimeStampWithFormatString(timeStamp, cls.tsFormat)
        else:
            # Call the full parser and store the format for next time
            timeStamp = cls.tsParser.parseTimeStamp(timeStamp)
            cls.tsFormat = cls.tsParser.lastTimeStampFormat
            return timeStamp