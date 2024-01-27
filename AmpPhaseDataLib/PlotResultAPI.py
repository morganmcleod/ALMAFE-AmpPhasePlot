'''
Data management API for Amplitude and Phase stability Results

Exposes the following data model:

+--------------+
| PlotResult   |
| +id          |
| +description |
| +timeStamp   |
| +tags        |    # a collection of name-value pairs, names given in Constants.py
+--------------+
    |
    |
    | 0..*
+------------+
| PlotImage  |
| +name      |
| +kind      |    # Enum defined in Constants.py
| +path      |
| +imageData |    # binary and/or a image file on disk;
+------------+
'''
from AmpPhaseDataLib.Constants import DataSource, PlotKind
from Database.PlotResultDatabase import PlotResultDatabase
from Database.PlotImageDatabase import PlotImageDatabase
from Database.Interface.PlotResult import PlotResult
import configparser

class PlotResultAPI(object):
    '''
    Data management API for Amplitude and Phase stability plot Results
    All parameters and returns values are Python builtins or enum, not implementation data structures.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__reset()
        self.__loadConfiguration()
        self.db = PlotResultDatabase(self.user, self.passwd, self.host, self.database, self.use_pure)
        self.imageDb = PlotImageDatabase(self.db.PLOT_RESULTS_TABLE, self.user, self.passwd, self.host, self.database, self.use_pure)
        
# PlotResult functions:
        
    def create(self, description, timeStamp = None):
        '''
        Create a new PlotResult record.
        :param description: str description of the result
        :param timeStamp: when measured.  Defaults to now()
        :return plotResultId int
        '''
        result = self.db.create(description, timeStamp)
        if not result:
            return None
        else:
            return result.plotResultId
    
    def retrieve(self, plotResultId):
        '''
        Retrieve a PlotResult record.
        :param plotResultId: int
        :return (plotResultId, description, timeStamp) if successful, None otherwise
        '''
        result = self.db.retrieve(plotResultId)
        if not result:
            return None
        else:
            return (plotResultId, result.description, result.timeStamp)
    
    def update(self, plotResultId, description = None, timeStamp = None):
        '''
        Update the description and/or timestamp for a PlotResult.
        :param plotResultId: int
        :param description: str
        :param timeStamp:   datetime
        :return the resultId if successful, None otherwise.
        '''
        result = PlotResult(plotResultId, description, timeStamp)
        if self.db.update(result):
            return plotResultId
        else:
            return None
        
    def delete(self, plotResultId):
        '''
        Delete a PlotResult and all of its PlotImages
        :param resultId: int
        '''
        self.db.delete(plotResultId)
    
    def setDataSource(self, plotResultId, dataSource, value):
        '''
        Set a DataSource tag for a PlotResult.
        :param resultId:   int
        :param dataSource: DataSource enum from Constants.py        
        :param value:      str or None to delete
        '''
        if not isinstance(dataSource, DataSource):
            raise ValueError('Use DataSource enum from Constants.py')
        self.db.setTags(plotResultId, { dataSource.value : value })
    
    def clearDataSource(self, plotResultId, dataSource):
        '''
        Clear a DataSource tag for a Result.
        :param resultId:   int
        :param dataSource: DataSource enum from Constants.py        
        '''
        self.setDataSource(plotResultId, dataSource, None)
    
    def getDataSource(self, plotResultId, dataSource):
        '''
        Retrieve a DataSource tag for a Result.
        :param resultId:   int
        :param dataSource: DataSource enum from Constants.py
        :return str value of the requested DataSource tag or None if not found
        '''
        if not isinstance(dataSource, DataSource):
            raise ValueError('Use DataSource enum from Constants.py')
        result = self.db.getTags(plotResultId, [dataSource.value])
        return result.get(dataSource.value, None)

    def getAllDataSources(self, plotResultId):
        '''
        Get all DataSource tags for a TimeSeries
        :param timeSeriesId: int
        :return dict of {DataSource : str}
        '''
        retrieved = self.db.getTags(plotResultId, [el.value for el in DataSource])
        result = {}
        # replace key str values with DataSource enum values:
        for tag, value in retrieved.items():
            result[DataSource(tag)] = value
        return result
        
# PlotImage functions:
        
    def insertPlotImage(self, plotResultId, imageData, name = None, kind = None, srcPath = None):
        '''
        Insert a PLotImage from binary image data.
        :param plotResultId: int PlotResult header to associate with the PlotImage
        :param imageData: binary image data in .png format
        :param name: str optional.
        :param kind: PlotKind enum from Constants.py
        :param srcPath: path source file on disk. Optional
        :return plotImageId int if successful, None otherwise. 
        '''
        if not imageData:
            raise ValueError("Must provide binary imageData")
        
        if kind:
            try:
                # convert from PlotKind enum to int:
                kind = kind.value
            except:
                try:
                    kind = int(kind)
                except:
                    raise ValueError("Use PlotKind enum from Constants.py or int.")

        plotImage = self.imageDb.create(plotResultId, imageData, name, kind, srcPath)
        if not plotImage:
            return None
        
        return plotImage.plotImageId

    def insertPlotImageFromFile(self, plotResultId, srcPath, name = None, kind = None):
        '''
        Insert a PlotImage from an image file.
        :param plotResultId: int PlotResult header to associate with the PlotImage
        :param srcPath: path to image file on disk.  Required.
        :param name: str optional.
        :param kind: PlotKind enum from Constants.py
        :return plotImageId int if successful, None otherwise. 
        '''
        if not srcPath:
            raise ValueError("Must provide a path to the image file")
        
        if kind:
            try:
                # convert from PlotKind enum to int:
                kind = kind.value
            except:
                try:
                    kind = int(kind)
                except:
                    raise ValueError("Use PlotKind enum from Constants.py or int.")
        
        with open(srcPath, 'rb') as file:
            imageData = file.read()
        
        plotImage = self.imageDb.create(plotResultId, imageData, name, kind, srcPath)
        if not plotImage:
            return None
        
        return plotImage.plotImageId

    def retrievePlotImage(self, plotImageId):
        '''
        Retrive plot image as binary data
        :param plotImageId: int
        :return (plotResultId, plotImageId, name, kind, path, imageData)
        '''
        plotImage = self.imageDb.retrieve(plotImageId)        
        if not plotImage:
            return None
        else:
            return (plotImage.plotResultId, 
                    plotImage.plotImageId, 
                    plotImage.name, 
                    PlotKind(plotImage.kind), 
                    plotImage.path, 
                    plotImage.imageData)

    def retrievePlotImageByKind(self, plotResultId, kind):
        '''
        Retrive plot image as binary data from kind
        :param plotImageId: int
        :return (plotResultId, plotImageId, name, kind, path, imageData)
        '''
        if kind:
            try:
                # convert from PlotKind enum to int:
                kind = kind.value
            except:
                try:
                    kind = int(kind)
                except:
                    raise ValueError("Use PlotKind enum from Constants.py or int.")
        plotImage = self.imageDb.retrieveByKind(None, kind, plotResultId)
        if not plotImage:
            return None
        else:
            return (plotImage.plotResultId,
                    plotImage.plotImageId,
                    plotImage.name,
                    PlotKind(plotImage.kind),
                    plotImage.path,
                    plotImage.imageData)

    def retrievePlotImages(self, plotResultId):
        '''
        Retrieve all the plot images associated with plotResultId:
        :param plotResultId: int
        :return list of (plotResultId, plotImageId, name, kind, path, imageData)
        '''
        plotImages = self.imageDb.retrieve(None, plotResultId)        
        if not plotImages:
            return None
        else:
            return [(plotImage.plotResultId, 
                     plotImage.plotImageId, 
                     plotImage.name, 
                     PlotKind(plotImage.kind), 
                     plotImage.path, 
                     plotImage.imageData) for plotImage in plotImages]
                    
    def retrievePlotImageToFile(self, plotImageId, targetPath):
        '''
        Retrieve a PlotImage and save to an image file.
        :param plotImageId: int
        :param targetPath: file name to create. Required.
        :return targetPath if successful, None otherwise
        '''
        plotImage = self.imageDb.retrievePlotImage(plotImageId)
        
        if not plotImage:
            return None
                
        with open(targetPath, 'wb') as file:
            file.write(plotImage.imageData)
    
        return targetPath
    
    def deletePlotImage(self, plotImageId):
        '''
        Delete a plotImage
        :param plotImageId: int
        '''
        self.imageDb.delete(plotImageId)
       
# private implementation methods...
        
    def __reset(self):
        '''
        Initialize all data members to just-constructed state.
        Called in constructor and retrieveTimeSeries()  
        '''
        pass
    
    def __loadConfiguration(self):
        '''
        load our configuration file
        '''
        self.host = None
        self.database = None 
        self.user = None
        self.passwd = None 
        self.use_pure = None
      
        config = configparser.ConfigParser()
        config.read("AmpPhaseDataLib.ini")
        databaseType = config['Configuration']['plotResultsDatabase']
        if databaseType == 'MySQL':
            self.host = config['MySQL']['host']
            self.database = config['MySQL']['database']
            self.user = config['MySQL']['user']
            self.passwd = config['MySQL']['passwd']
            self.use_pure = True if config['MySQL'].get('use_pure', False) else False
        else:
            raise NotImplementedError('Databases other than MySQL not implemented in PlotResultAPI.')
