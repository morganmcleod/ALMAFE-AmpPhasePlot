import Database.Interface.Result as RI
import Database.Interface.Tags as TI
import Database.Driver.MySQL as driver
import Database.TagsDatabase as TagsDB
from AmpPhaseDataLib.Constants import PlotKind
from itertools import zip_longest

class ResultDatabase(RI.ResultInterface, TI.TagsInterface):
    '''
    MySQL implementation of Database.Interface.Result.ResultInterface
    '''
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    RESULTS_TABLE = 'AmpPhase_Results'
    PLOTS_TABLE = 'AmpPhase_Plots'
    TRACES_TABLE = 'AmpPhase_Traces'
    TRACE_XYDATA_TABLE = 'AmpPhase_TraceXYData'
    RESULT_TAGS_TABLE = 'AmpPhase_ResultTags'
    PLOT_TAGS_TABLE = 'AmpPhase_PlotTags'

    def __init__(self, user, passwd = None, host = '127.0.0.1', database = 'AmpPhaseData'): 
        '''
        Constructor
        '''
        connectionInfo = {
            'user' : user,
            'passwd' : passwd,
            'host' : host,
            'database' : database
        }
        self.database = database
        self.DB = driver.DriverMySQL(connectionInfo)
        self.tagsDB = TagsDB.TagsDatabase(self.DB)
        self.createTables()

#// ResultInterface create, retrieve, update, delete...

    def createResult(self, description = None, timeStamp = None):
        '''
        Create a new Result object in the database
        :param description: str
        :param timeStamp: datetime to associate with the Result.  Defaults to now(). 
        :return Result object if succesful, None otherwise.
        '''
        q = "INSERT INTO `{0}` (`description`".format(self.RESULTS_TABLE)
        if (timeStamp):
            q += ", `timeStamp`"
        q += ") VALUES ("
        q += "'{0}'".format(description) if description else "NULL"
        if (timeStamp):
            q += ", '{0}'".format(timeStamp.strftime(self.TIMESTAMP_FORMAT))
        q += ");"
        
        self.DB.execute(q, commit = True)
        self.DB.execute("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.Result(row[0], description, timeStamp)
    
    def retrieveResult(self, resultId):
        '''
        Retrieve a Result object from the database
        :param resultId: int to retrieve
        :return Result object if succesful, None otherwise.
        '''
        q = "SELECT `description`, `timeStamp` FROM `{0}` WHERE `keyId` = '{1}';".format(self.RESULTS_TABLE, resultId)
        self.DB.execute(q)
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.Result(resultId, row[0], row[1])

    def updateResult(self, result):
        '''
        Update an existing Result object in the database
        :param Result: object to update
        :return Result object if successful, None otherwise.
        '''
        q = "UPDATE `{0}` SET `Description` = '{1}'".format(self.RESULTS_TABLE, result.description)
        if result.timeStamp:
            q += ", `timeStamp` = '{0}'".format(result.timeStamp.strftime(self.TIMESTAMP_FORMAT))
        q += " WHERE `keyId` = '{0}';".format(result.resultId)
        if self.DB.execute(q, commit = True):
            return result
        else:
            return None
    
    def deleteResult(self, resultId):
        '''
        Delete a Result object from the database
        Underlying Plots, PlotImages, Traces, and Tags are deleted via ON DELETE CASCADE
        :param resultId: int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = '{1}';".format(self.RESULTS_TABLE, resultId)
        self.DB.execute(q, commit = True)

    def setResultTags(self, resultId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Result:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param resultId: int of the Result to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        self.tagsDB.setTags(resultId, self.RESULT_TAGS_TABLE, 'fkResults', tagDictionary)
        
    def getResultTags(self, resultId, tagNames = None):       
        '''
        Retrieve tags on the specified Result:
        :param resultId: int of the Result to query
        :param tagNames: list of strings or None, indicating fetch all tags
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        return self.tagsDB.getTags(resultId, self.RESULT_TAGS_TABLE, 'fkResults', tagNames)

#// Plot create, delete, update, retrieve...

    def createPlot(self, resultId, kind = None):
        '''
        Create a Plot associated with the specified Result:
        :param resultId: int of the Result to associate with the Plot
        :param kind: PlotKind specify what type of plot it is
        :return Plot object if successful, None otherwise.
        '''
        q = "INSERT INTO `{0}` (`fkResults`, `plotKind`) VALUES ({1}, {2});".format(self.PLOTS_TABLE, resultId, kind.value)
        self.DB.execute(q, commit = True)
        self.DB.execute("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.Plot(row[0], resultId, kind)
    
    def retrievePlot(self, plotId):
        '''
        Retrieve a specified Plot:
        :param plotId: int of the plot to retrieve
        :return Plot object if successful, None otherwise.
        '''
        q = "SELECT `fkResults`, `plotKind` FROM `{0}` WHERE `keyId` = {1};".format(self.PLOTS_TABLE, plotId)
        self.DB.execute(q)
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.Plot(plotId, row[0], PlotKind(row[1]))
        
    def deletePlot(self, plotId):
        '''
        Delete the specified Plot. 
        Underlying PlotImages, Traces, and Tags are deleted via ON DELETE CASCADE
        :param plotId: int of the plot to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.PLOTS_TABLE, plotId)
        self.DB.execute(q, commit = True)
        
    def getAllPlots(self, resultId):
        '''
        Retrieve all plots associated with the given resultId 
        :param resultId: int
        :return list of Plot objects
        '''
        q = "SELECT `keyId`, `fkResults`, `plotKind`, `timeStamp` FROM {0} WHERE fkResults = {1};".format(
            self.PLOTS_TABLE, resultId)
        self.DB.execute(q)
        rows = self.DB.fetchall()
        result = []
        for row in rows:
            result.append(RI.Plot(row[0], row[1], row[2], row[3]))
        return result
        
    def setPlotTags(self, plotId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Plot:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param plotId: int of the Plot to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        self.tagsDB.setTags(plotId, self.PLOT_TAGS_TABLE, 'fkPlots', tagDictionary)
        
    def getPlotTags(self, plotId, tagNames):       
        '''
        Retrieve tags on the specified Plot:
        :param plotId: int of the Plot to query
        :param tagNames: list of strings or None, indicating fetch all tags
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        return self.tagsDB.getTags(plotId, self.PLOT_TAGS_TABLE, 'fkPlots', tagNames)

#// Trace create, retrieve, update, delete...

    def createTrace(self, plotId, xyData, name = None, legend = None):
        '''
        Create a trace on the specified Plot
        :param plotId: Plot to which the trace belongs
        :param xyData: tuple of float lists ([x], [y], [yError]) with yError optional
        :param name: trace name
        :param legend: trace legend for display
        :return Trace object if successful, None otherwise
        '''
        q = "INSERT INTO `{0}` (`fkPlots`, `name`, `legend`) VALUES ({1}, ".format(self.TRACES_TABLE, plotId)
        q += "'{0}'".format(name) if name else "NULL"
        q += ", "
        q += "'{0}'".format(legend) if legend else "NULL"
        q += ");"
        
        if not self.DB.execute(q, commit = False):
            return None
        
        self.DB.execute("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        traceId = row[0]
        
        q = "INSERT INTO `{0}` (`fkTraces`, `XValue`, `YValue`, `YErrSize`) VALUES ".format(self.TRACE_XYDATA_TABLE)

        yError = xyData[2] if len(xyData) and xyData[2] else []  
        firstTime = True
        for x, y, err in zip_longest(xyData[0], xyData[1], yError):
            if firstTime:
                q += "("
                firstTime = False
            else:
                q += ", ("
            q += "{0}, {1}, {2}, {3})".format(traceId, x, y, err if err else 0) 
        q += ";"        
        
        if not self.DB.execute(q, commit = True):
            self.DB.rollback()
            return None
        
        return RI.Trace(traceId, plotId, xyData, name, legend)
    
    def retrieveTrace(self, traceId):
        '''
        Retrieve the specified trace
        :param traceId int to retrieve
        :return Trace object if successful, None otherwise
        '''
        q = "SELECT `fkPlots`, `name`, `legend` FROM {0} WHERE `keyId` = {1};".format(self.TRACES_TABLE, traceId)
        self.DB.execute(q)
        row = self.DB.fetchone()
        if not row:
            return None
        plotId, name, legend = row[0], row[1], row[2]
        
        q = "SELECT `XValue`, `YValue`, `YErrSize` FROM {0} WHERE `fkTraces` = {1} ORDER BY `keyId`;".format(
            self.TRACE_XYDATA_TABLE, traceId)
        self.DB.execute(q)
        result = self.DB.fetchall()
        
        x = []
        y = []
        yError = []
        if result:
            for row in result:
                x.append(row[0])
                y.append(row[1])
                yError.append(row[2])

        return RI.Trace(traceId, plotId, (x, y, yError), name, legend)

    def retrieveTraces(self, plotId):
        '''
        Retrieve all traces associated with a plotId
        :param traceId int to retrieve
        :return list of Trace objects if successful, None otherwise.
        '''
        q = "SELECT `keyId`, `name`, `legend` FROM {0} WHERE `fkPlots` = {1};".format(self.TRACES_TABLE, plotId)
        self.DB.execute(q)
        rows = self.DB.fetchall()
        if not rows:
            return None
        
        traces = []
        traceIds = ""
        for row in rows:
            traceId, name, legend = row[0], row[1], row[2]
            traces += RI.Trace(traceId, plotId, None, name, legend)
            if traceIds:
                traceIds += ", "
            traceIds += "'{0}'".format(traceId)
        
        q = "SELECT `fkTraces`, `XValue`, `YValue`, `YErrSize` FROM {0} WHERE `fkTraces` in ({1}) ORDER BY `keyId`;".format(
            self.TRACE_XYDATA_TABLE, traceIds)
        self.DB.execute(q)
        result = self.DB.fetchall()
        
        #append a dummy value to the end so we can store the last set inside the loop:
        result.append(('0', '0', '0', '0'))
        
        #start with empty xyData component lists:
        xArray = []
        yArray = []
        yError = []
        
        #use result to update traces[]: 
        if result:
            #to detect new traceId in result:
            lastId = None
            for row in result:
                traceId, x, y, err = row[0], row[1], row[2], row[3]
                
                #detect new traceId:
                if traceId != lastId:
                    #not first time:
                    if lastId:
                        #find matching Trace object in traces[] and assign:
                        trace = next((tr for tr in traces if tr.traceId == lastId), None)
                        trace.xyData = (xArray, yArray, yError)
                        #empty the component lists:
                        xArray = []
                        yArray = []
                        yError = []
                    #update for next iterations:
                    lastId = traceId
                
                # only append if it's not the dummy value appended above:
                if traceId:
                    xArray.append(x)
                    yArray.append(y)
                    yError.append(err)
        
        return traces
    
    def deleteTrace(self, traceId):
        '''
        Delete the specified trace.
        Underlying TraceXYData are deleted via ON DELETE CASCADE
        :param traceId int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.TRACES_TABLE, traceId)
        if not self.DB.execute(q, commit = True):
            self.DB.rollbackTransaction()

#// Database helper and private methods...
    
    def createTables(self):
        self.DB.execute("USE {0};".format(self.database))
        
        # Results table
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `description` TEXT NULL DEFAULT NULL,
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`)
                ) ENGINE=InnoDB;
            """.format(self.RESULTS_TABLE))

        # Plots table        
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `plotKind` TINYINT NOT NULL DEFAULT '0',
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`),
                FOREIGN KEY (`fkResults`) REFERENCES {1}(`keyId`) ON DELETE CASCADE,
                INDEX `fkResults` (`fkResults`)
                ) ENGINE=InnoDB;
            """.format(self.PLOTS_TABLE, self.RESULTS_TABLE))

        # Traces table        
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `name` TEXT NULL DEFAULT NULL,
                `legend` TEXT NULL DEFAULT NULL,
                PRIMARY KEY (`keyId`),
                FOREIGN KEY (`fkPlots`) REFERENCES {1}(`keyId`) ON DELETE CASCADE,
                INDEX `fkPlots` (`fkPlots`)
                ) ENGINE=InnoDB;
            """.format(self.TRACES_TABLE, self.PLOTS_TABLE))

        # TraceXYData table
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkTraces` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `XValue` FLOAT NOT NULL,
                `YValue` FLOAT NOT NULL,
                `YErrSize` FLOAT NOT NULL DEFAULT '0' COMMENT '+/- error bar size',
                PRIMARY KEY (`keyId`),
                FOREIGN KEY (`fkTraces`) REFERENCES {1}(`keyId`) ON DELETE CASCADE,
                INDEX `fkTraces` (`fkTraces`)
                ) ENGINE=InnoDB;
            """.format(self.TRACE_XYDATA_TABLE, self.TRACES_TABLE))

        # ResultTags table
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkResults` (`fkResults`),
                FOREIGN KEY (`fkResults`) REFERENCES {1}(`keyId`) ON DELETE CASCADE
                ) ENGINE=InnoDB;
            """.format(self.RESULT_TAGS_TABLE, self.RESULTS_TABLE))

        # PlotTags table        
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkPlots` (`fkPlots`),          
                FOREIGN KEY (`fkPlots`) REFERENCES {1}(`keyId`) ON DELETE CASCADE
                ) ENGINE=InnoDB;
            """.format(self.PLOT_TAGS_TABLE, self.PLOTS_TABLE))
        
    def deleteTables(self):
        self.DB.execute("USE {0};".format(self.database))
        self.DB.execute("DROP TABLE `{0}`".format(self.PLOT_TAGS_TABLE))
        self.DB.execute("DROP TABLE `{0}`".format(self.RESULT_TAGS_TABLE))
        self.DB.execute("DROP TABLE `{0}`".format(self.TRACE_XYDATA_TABLE))
        self.DB.execute("DROP TABLE `{0}`".format(self.TRACES_TABLE))
        self.DB.execute("DROP TABLE `{0}`".format(self.PLOTS_TABLE))
        self.DB.execute("DROP TABLE `{0}`".format(self.RESULTS_TABLE))
