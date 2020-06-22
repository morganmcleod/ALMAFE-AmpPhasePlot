'''
Interface classes for storage and retrieval of Result, Plot, and Trace objects.
'''

from AmpPhaseDataLib.Constants import PlotKind
from abc import ABC, abstractmethod
from datetime import datetime

class Result:
    '''
    a Result has
    values:
        resultId:int, description, timeStamp
    tags:
        zero or more name-value pairs
    aggregates:
        zero or more Plots
    '''
    def __init__(self, resultId, description = None, timeStamp = None):
        self.resultId = resultId
        self.description = str(description if description else "")
        self.timeStamp = timeStamp if timeStamp else datetime.now()

class Plot:
    '''
    a Plot has
    values:
        plotId, PlotKind
    tags:
        zero or more name-value pairs
    aggregates:
        zero or more Traces
        zero or more PlotImages
    references:
        one Result via resultId
    '''
        
    def __init__(self, plotId, ResultId, kind = PlotKind.NONE):
        self.plotId = plotId
        self.resultId = ResultId
        self.kind = kind
        
class Trace:
    '''
    a Trace has
    values: 
        traceId:int, name, legend, 
        xyData: float list of tuples (x, y) or (x, y, yError)
    references:
        one Plot via plotId
    '''
    def __init__(self, traceId, plotId, xyData, name = None, legend = None):
        self.traceId = traceId
        self.plotId = plotId
        self.xyData = xyData
        self.name = str(name) if name else ""
        self.legend = str(legend) if legend else self.name
        
class ResultInterface(ABC):
    '''
    Defines the interface for storing and retrieving Result, Plot, Trace objects defined above.     
    '''
    
#// Result methods
    
    @abstractmethod
    def createResult(self, description = None, timeStamp = None):
        '''
        Create a new Result object in the database
        :param description: str
        :param timeStamp: datetime to associate with the Result.  Defaults to now(). 
        :return Result object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def retrieveResult(self, resultId):
        '''
        Retrieve a Result object from the database
        :param resultId: int to retrieve
        :return Result object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def updateResult(self, result):
        '''
        Update an existing Result object in the database
        :param result: object to update
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

#// Plot methods
    
    @abstractmethod
    def createPlot(self, resultId, kind):
        '''
        Create a Plot associated with the specified Result:
        :param resultId: int of the Result to associate with the Plot
        :param kind: PlotKind specify what type of plot it is
        :return Plot object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def retrievePlot(self, plotId):
        '''
        Retrieve a specified Plot:
        :param plotId: int of the plot to retrieve
        :return Plot object if successful, None otherwise.
        '''
        
    # no updatePlot() needed yet...
    
    @abstractmethod
    def deletePlot(self, plotId):
        '''
        Delete the specified Plot
        :param plotId: int of the plot to delete
        '''

#// Trace methods
    
    @abstractmethod        
    def createTrace(self, plotId, xyData, name = None, legend = None):
        '''
        Create a trace on the specified Plot
        :param plotId: Plot to which the trace belongs
        :param xyData: float list of tuples (x, y) or (x, y, yError)
        :param name: trace name
        :param legend: trace legend for display
        :return Trace object if successful, None otherwise
        '''
        pass
        
    @abstractmethod        
    def retrieveTrace(self, traceId):
        '''
        Retrieve the specified trace
        :param traceId int to retrieve
        :return Trace object if successful, None otherwise
        '''
        pass
    
    # no updateTrace needed yet...
    
    @abstractmethod        
    def deleteTrace(self, traceId):
        '''
        Delete the specified trace
        :param traceId int to delete
        '''
        pass
        
