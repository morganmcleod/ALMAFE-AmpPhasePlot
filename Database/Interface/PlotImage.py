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
    def __init__(self, plotId, plotImageId, imageData, name = None, path = None):
        self.plotId = plotId
        self.plotImageId = plotImageId
        self.name = str(name) if name else ""
        self.path = str(path) if path else ""
        self.imageData = imageData
        
class PlotImageInterface(ABC):
    '''
    Defines the interface for storing and retrieving PlotImage objects defined above.     
    '''
    @abstractmethod
    def createPlotImage(self, plotId, imageData, name = None, path = None):
        '''
        Create a new PlotImage object in the database
        :param plotId:    Plot object to assocate this image with
        :param imageData: Binary image data
        :param name: str  
        :param path: str may be used for filesystem storage
        :return PlotImage object if successful, None otherwise
        '''
        pass
    
    @abstractmethod
    def retrievePlotImage(self, plotImageId):
        '''
        Retrieve the specified PlotImage object from the database
        :param plotImageId: to retrieve
        :return PlotImage object if successful, None otherwise
        '''
        pass

    # no updatePlotImage for now.
    
    @abstractmethod
    def deletePlotImage(self, plotImageId):
        '''
        Delete the specified PlotImage object from the database
        :param plotImageId: to delete
        '''
        pass
