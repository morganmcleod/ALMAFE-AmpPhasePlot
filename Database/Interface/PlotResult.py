'''
Interface classes for storage and retrieval of Result, Plot, and Trace objects.
'''

from abc import ABC, abstractmethod
from datetime import datetime

class PlotResult:
    '''
    a Result has
    values:
        plotResultId:int, description, timeStamp
    tags:
        zero or more name-value pairs
    aggregates:
        zero or more PlotImages
    '''
    def __init__(self, plotResultId, description = None, timeStamp = None):
        self.plotResultId = plotResultId
        self.description = str(description if description else "")
        self.timeStamp = timeStamp if timeStamp else datetime.now()
       
class PlotResultInterface(ABC):
    '''
    Defines the interface for storing and retrieving Result, Plot, Trace objects defined above.     
    '''
    
# PlotResult methods
    
    @abstractmethod
    def create(self, description = None, timeStamp = None):
        '''
        Create a new PlotResult object in the database
        :param description: str
        :param timeStamp: datetime to associate with the Result.  Defaults to now(). 
        :return PlotResult object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def retrieve(self, plotResultId):
        '''
        Retrieve a PlotResult object from the database
        :param plotResultId: int to retrieve
        :return PlotResult object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def update(self, plotResult):
        '''
        Update an existing PlotResult object in the database
        :param plotResult: object to update
        :return PlotResult object if successful, None otherwise.
        '''
        pass
    
    @abstractmethod
    def delete(self, plotResultId):
        '''
        Delete a PlotResult object from the database
        :param plotResultId: int to delete
        '''
        pass
