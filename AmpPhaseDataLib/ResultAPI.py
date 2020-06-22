'''
Data management API for Amplitude and Phase stability Results

Exposes the following data model:

+--------------+
| Result       |
| +id          |
| +description |
| +timeStamp   |
| +tags        |
+--------------+
    |
    |
    | 0..*
+--------+            +------------+
| Plot   |       0..* | PlotImage  |
| +kind  |------------| +name      |
| +tags  |            | +path      |
---------+            | +imageData |
    |                 +------------+
    |
    | 0..*
+---------+
| Trace   |
| +name   |
| +legend | 
| +XYData |
+---------+

Where tags is a collection of name-value pairs, names given in Constants.py
kind is enum defined in Constants.py
imageData is binary and/or a image file on disk;
XYData is float list of tuples (x, y, yError)
'''
from AmpPhaseDataLib.Constants import PlotKind, DataStatus, DataSource, PlotElement
from Database import ResultDatabase
from Database import PlotImageDatabase
from Database.Interface.Result import Result
import configparser

class ResultAPI(object):
    '''
    Data management API for Amplitude and Phase stability Results
    All parameters and returns values are Python builtins or enum, not implementation data structures.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__reset()
        self.__loadConfiguration()
        self.db = ResultDatabase.ResultDatabase(self.user, self.passwd, self.host, self.database)
        self.imageDb = PlotImageDatabase.PlotImageDatabase(self.user, self.passwd, self.host, self.database)
        
#// Result functions:
        
    def createResult(self, description, timeStamp = None):
        '''
        Create a new result record.
        :param description: str description of the result
        :param timeStamp: when measured.  Defaults to now()
        :return resultId int
        '''
        result = self.db.createResult(description, timeStamp)
        if not result:
            return None
        else:
            return result.resultId
    
    def retrieveResult(self, resultId):
        '''
        Retrieve a result record.
        :param resultId: int
        :return (resultId, description, timeStamp) if successful, None otherwise
        '''
        result = self.db.retrieveResult(resultId)
        if not result:
            return None
        else:
            return (resultId, result.description, result.timeStamp)
    
    def updateResult(self, resultId, description = None, timeStamp = None):
        '''
        Update the description and/or timestamp for a Result.
        :param resultId:    int
        :param description: str
        :param timeStamp:   datetime
        :return the resultId if successful, None otherwise.
        '''
        result = Result(resultId, description, timeStamp)
        if self.db.updateResult(result):
            return resultId
        else:
            return None
        
    def deleteResult(self, resultId):
        '''
        Delete a result and all of its Plots, Traces, and PlotImages
        :param resultId: int
        '''
        self.db.deleteResult(resultId)
    
    def setResultDataStatus(self, resultId, dataStatus):
        '''
        Set a DataStatus tag for a Result.
        :param resultId:   int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise ValueError('Use DataStatus enum from Constants.py')
        self.db.setResultTags(resultId, { dataStatus.value : "1" })
    
    def getResultDataStatus(self, resultId, dataStatus):
        '''
        Get whether the given dataStatus tag has been set for a result
        :param resultId:   int
        :param dataStatus: DataStatus enum from Constants.py
        :return boolean
        '''
        if not isinstance(dataStatus, DataStatus):
            raise ValueError('Use DataStatus enum from Constants.py')
        result = self.db.getResultTags(resultId, [dataStatus.value])
        if not result:
            return False
        else:
            return True if result.get(dataStatus.value) else False
        
    def clearResultDataStatus(self, resultId, dataStatus):
        '''
        Clear a DataStatus tag for a Result.
        :param resultId:   int
        :param dataStatus: DataStatus enum from Constants.py
        '''
        if not isinstance(dataStatus, DataStatus):
            raise ValueError('Use DataStatus enum from Constants.py')
        self.db.setResultTags(resultId, { dataStatus.value : None })
    
    def setResultDataSource(self, resultId, dataSource, value):
        '''
        Set a DataSource tag for a Result.
        :param resultId:   int
        :param dataSource: DataSource enum from Constants.py        
        :param value:      str or None to delete
        '''
        if not isinstance(dataSource, DataSource):
            raise ValueError('Use DataSource enum from Constants.py')
        self.db.setResultTags(resultId, { dataSource.value : value })
    
    def clearResultDataSource(self, resultId, dataSource):
        '''
        Clear a DataSource tag for a Result.
        :param resultId:   int
        :param dataSource: DataSource enum from Constants.py        
        '''
        self.setResultDataSource(resultId, dataSource, None)
    
    def getResultDataSource(self, resultId, dataSource):
        '''
        Retrieve a DataSource tag for a Result.
        :param resultId:   int
        :param dataSource: DataSource enum from Constants.py
        :return str value of the requested DataSource tag or None if not found
        '''
        if not isinstance(dataSource, DataSource):
            raise ValueError('Use DataSource enum from Constants.py')
        result = self.db.getResultTags(resultId, [dataSource.value])
        return result.get(dataSource.value, None)
        
        
#// Plot (header) functions
    
    def createPlot(self, resultId, kind):
        '''
        Create a Plot header referencing a Result 
        :param resultId:
        :param kind:
        :return plotId int if succesful, otherwise None
        '''
        if not isinstance(kind, PlotKind):
            raise ValueError('Use PlotKind enum from Constants.py')
        plot = self.db.createPlot(resultId, kind)
        if not plot:
            return None
        else:
            return plot.plotId

    def retrievePlot(self, plotId):
        '''
        Retrieve a plot header
        :param plotId: int
        return (plotId, kind) if successful, otherwise None
        '''
        plot = self.db.retrievePlot(plotId)
        if not plot:
            return None
        else:
            return (plotId, plot.kind)
    
    def deletePlot(self, plotId):
        '''
        Delete a plot header and all of its contained Traces and PlotImages
        :param plotId:
        '''
        self.db.deletePlot(plotId)   

    def setPlotElement(self, plotId, plotElement, value):
        '''
        Set the value of a plot element, overriding the default value
        :param plotId: int
        :param plotElement: enum from Constants.py
        :param value: str or None to delete
        '''
        if not isinstance(plotElement, PlotElement):
            raise ValueError('Use PlotElement enum from Constants.py')
        self.db.setPlotTags(plotId, { plotElement.value : value })

    def clearPlotElement(self, plotId, plotElement):
        '''
        Clear the value of a plot element
        :param plotId: int
        :param plotElement: enum from Constants.py
        '''
        self.setPlotElement(plotId, plotElement, None)

    def getPlotElement(self, plotId, plotElement):
        '''
        Get the value of a plot element
        :param plotId:
        :param plotElement:
        :return str the value
        '''
        if not isinstance(plotElement, PlotElement):
            raise ValueError('Use PlotElement enum from Constants.py')
        result = self.db.getPlotTags(plotId, [plotElement.value])
        return result.get(plotElement.value, None)

#// Plot Trace functions:
    
    def createTrace(self, plotId, xyData, name, legend = None):
        '''
        Create a trace associated with a Plot
        :param plotId: int Plot to which to add the trace.
        :param xyData: float list of tuples (x, y) or (x, y, yError)
        :param name: str
        :param legend: str, defaults to same as name
        :return traceId int
        '''
        trace = self.db.createTrace(plotId, xyData, name, legend)
        if not trace:
            return None
        else:
            return trace.traceId
        
    def retrieveTrace(self, traceId):
        '''
        Retrieve a trace.
        :param traceId: int
        :return (traceId, xyData, name, legend) if successful, None otherwise.
        '''
        trace = self.db.retrieveTrace(traceId)
        if not trace:
            return None
        else:
            return (traceId, trace.xyData, trace.name, trace.legend)
    
    def deleteTrace(self, traceId):
        '''
        Delete a trace.
        :param traceId: int
        '''
        self.db.deleteTrace(traceId)
        
#// Plot Image functions:
        
    def insertPlotImageFromFile(self, plotId, srcPath, name = None):
        '''
        Insert a PlotImage from an image file.
        :param plotId: int Plot header to associate with the PlotImage
        :param srcPath: path to image file on disk.  Required.
        :param name: str optional.
        :return plotImageId int if successful, None otherwise. 
        '''
        if not srcPath:
            raise ValueError("Must provide a path to the image file")
        
        with open(srcPath, 'rb') as file:
            imageData = file.read()
        
        plotImage = self.imageDb.createPlotImage(plotId, imageData, name, srcPath)
        if not plotImage:
            return None
        
        return plotImage.plotImageId

    def retrievePlotImage(self, plotImageId):
        '''
        Retrive plot image as binary data
        :param plotImageId: int
        :return (plotId, plotImageId, name, path, imageData)
        '''
        plotImage = self.imageDb.retrievePlotImage(plotImageId)
        
        if not plotImage:
            return None
        else:
            return (plotImage.plotId, plotImage.plotImageId, plotImage.name, plotImage.path, plotImage.imageData)
        
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
        self.imageDb.deletePlotImage(plotImageId)
       
#// private implementation methods...
        
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
      
        config = configparser.ConfigParser()
        config.read("AmpPhaseDataLib.ini")
        databaseType = config['Configuration']['resultsDatabase']
        if databaseType == 'MySQL':
            self.host = config['MySQL']['host']
            self.database = config['MySQL']['database']
            self.user = config['MySQL']['user']
            self.passwd = config['MySQL']['passwd']
        else:
            raise NotImplementedError('Databases other than MySQL not implemented in ResultAPI.')

        databaseType = config['Configuration']['plotImageDatabase']
        if databaseType == 'MySQL':
            self.host = config['MySQL']['host']
            self.database = config['MySQL']['database']
            self.user = config['MySQL']['user']
            self.passwd = config['MySQL']['passwd']
        else:
            raise NotImplementedError('Databases other than MySQL not implemented in ResultAPI.')
