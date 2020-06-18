'''
Result storage and retrieval...

a Result has
values:
    resultId:int, description, timeStamp
tags:
    zero or more name-value pairs
aggregates:
    zero or more Plots
    
a Plot has
values:
    kind : PlotType (TimeSeries, AllanVar, AllanDev, PowerSpectrum)
tags:
    zero or more name-value pairs
aggregates:
    zero or more Traces
    zero or more PlotImages
    
a Trace has
values: 
    traceId:int, legend, xyData
    
a PlotImage has
values:
    name, path    
'''

from abc import ABC, abstractmethod
from datetime import datetime

class Result:
    def __init__(self, resultId, description = None, timeStamp = None):
        self.resultId = resultId
        self.description = description
        self.timeStamp = timeStamp
        if not self.timeStamp:
            self.timeStamp = datetime.now()
        
class Plot:
    KIND_NONE = 0
    KIND_TIMESERIES = 1
    KIND_ALLANVAR = 2
    KIND_ALLANDEV = 3
    KIND_PWRSPECTRUM = 4
        
    def __init__(self, ResultId, plotId, kind = KIND_NONE):
        self.resultId = ResultId
        self.plotId = plotId
        self.kind = kind
        
class Trace:
    def __init__(self, plotId, name, xyData, legend = None):
        self.plotId = plotId
        self.name = name
        self.xyData = xyData
        self.legend = legend
        if not self.legend:
            self.legend = self.name
    
class PlotImage:
    def __init__(self, plotId, name = None, path = None, keyId = None):
        self.plotId = plotId
        self.name = name
        self.path = path
        self.keyId = keyId
        
class ResultInterface(ABC):
    '''
    Defines the interface for storing and retrieving Result objects defined above.     
    '''
    @abstractmethod
    def createResult(self, description = None, timeStamp = None):
        '''
        Create a new Result object in the database
        :param description: str
        :param timeStamp: datetime to associate with the Result.  Defaults to now(). 
        :return Result object if succesful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def retrieveResult(self, resultId):
        '''
        Retrieve a Result object from the database
        :param resultId: int to retrieve
        :return Result object if succesful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def updateResult(self, Result):
        '''
        Update an existing Result object in the database
        :param Result: object to update
        :return Result object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def deleteResult(self, resultId):
        '''
        Delete a Result object from the database
        :param resultId: int to delete
        '''
        pass
    
    @abstractmethod
    def setResultTags(self, resultId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Result:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param resultId: int of the Result to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        pass
        
    @abstractmethod
    def getResultTags(self, resultId, tagNames):       
        '''
        Retrieve tags on the specified Result:
        :param resultId: int of the Result to query
        :param tagNames: list of strings
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        pass
    
    @abstractmethod
    def createPlot(self, resultId, kind = None):
        '''
        Create a Plot associated with the specified Result:
        :param resultId: int of the Result to associate with the Plot
        :param kind: Plot.KIND* specify what type of plot it is
        :return Plot object if succesful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def retrievePlot(self, resultId, kind = None, plotId = None):
        '''
        Retrieve a Plot associated with the specified Result:
        Can search on kind or plotId so one or the other must be given.
        :param resultId: int of the Result
        :param kind: Plot.KIND* specify which plot to retrieve
        :param plotId: int of the plot to retrieve
        :return Plot object if succesful, None otherwise.
        '''
        
    # no updatePlot() needed yet...
    
    @abstractmethod
    def deletePlot(self, resultId, kind = None, plotId = None):
        '''
        Delete a Plot associated with the specified Result
        Can search on kind or plotId so one or the other must be given.
        :param resultId: int of the Result
        :param kind: Plot.KIND* specify which plot(s) to delete
        :param plotId: plotId: int of the plot to delete
        '''
    
    @abstractmethod
    def setPlotTags(self, plotId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Plot:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param plotId: int of the Plot to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        pass
        
    @abstractmethod
    def getPlotTags(self, plotId, tagNames):       
        '''
        Retrieve tags on the specified Plot:
        :param plotId: int of the Plot to query
        :param tagNames: list of strings
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        pass
    
    @abstractmethod        
    def createTrace(self, plotId, xyData, name = None, legend = None):
        pass
        
    @abstractmethod        
    def retrieveTrace(self, plotId, name):
        pass
    
    @abstractmethod        
    def updateTrace(self, trace):
        pass
    
    @abstractmethod        
    def deleteTrace(self, plotId, name):
        pass
        
