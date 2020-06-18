'''
Interface classes for storage and retrieval of PlotImage objects.

a PlotImage has
values:
    plotImageId: int, name, path
references:
    one Plot via plotId
'''
from abc import ABC, abstractmethod

class PlotImage:
    def __init__(self, plotId, plotImageId, name = None, path = None):
        self.plotImageId = plotImageId
        self.plotId = plotId
        self.name = name
        self.path = path

class PlotImageInterface(ABC):
    '''
    Defines the interface for storing and retrieving PlotImage objects defined above.     
    '''
    @abstractmethod
    def createPlotImage(self, plotId, name = None, path = None):
        '''
        Create a new PlotImage object in the database
        :param name: str  
        :param path: str may be used for filesystem storage
        :return PlotImage object if successful, None otherwise
        '''
        pass
    
    @abstractmethod
    def retrievePlotImage(self, plotId):
        '''
        Retrieve the specified PlotImage object from the database
        :param plotId: to retrieve
        :return PlotImage object if successful, None otherwise
        '''
        pass

    # no updatePlotImage for now.
    
    @abstractmethod
    def deletePlotImage(self, plotId):
        '''
        Delete the specified PlotImage object from the database
        :param plotId: to delete
        '''
        pass
