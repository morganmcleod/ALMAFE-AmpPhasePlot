'''
Interface classes for storage and retrieval of PlotImage objects.

a PlotImage has
values:
    plotImageId: int, name, kind, path
references:
    one PlotResult via plotResultId
'''
from abc import ABC, abstractmethod

class PlotImage:
    def __init__(self, plotResultId, plotImageId, imageData, name = None, kind = None, path = None):
        self.plotResultId = plotResultId
        self.plotImageId = plotImageId
        self.name = str(name) if name else ""
        self.kind = int(kind) if kind else 0
        self.path = str(path) if path else ""
        self.imageData = imageData
        
class PlotImageInterface(ABC):
    '''
    Defines the interface for storing and retrieving PlotImage objects defined above.     
    '''
    @abstractmethod
    def create(self, plotResultId, imageData, name = None, kind = None, path = None):
        '''
        Create a new PlotImage object in the database
        :param plotResultId:  PlotResult object to assocate this image with
        :param imageData: Binary image data
        :param name: str  
        :param kind: PlotKind enum from Constants.py
        :param path: str may be used for filesystem storage
        :return PlotImage object if successful, None otherwise
        '''
        pass
    
    @abstractmethod
    def retrieve(self, plotImageId):
        '''
        Retrieve the specified PlotImage object from the database
        :param plotImageId: to retrieve
        :return PlotImage object if successful, None otherwise
        '''
        pass

    # no updatePlotImage for now.
    
    @abstractmethod
    def delete(self, plotImageId):
        '''
        Delete the specified PlotImage object from the database
        :param plotImageId: to delete
        '''
        pass
