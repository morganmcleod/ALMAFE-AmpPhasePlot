import Database.Interface.Result as RI
import Database.Interface.Tags as TI
import Database.Driver.MySQL as driver

class ResultDatabase(RI.ResultInterface, TI.TagsInterface):
    '''
    MySQL implementation of Database.Interface.Result.ResultInterface
    '''
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    RESULTS_TABLE = 'Results'
    PLOTS_TABLE = 'Plots'
    TRACES_TABLE = 'Traces'
    TRACE_XYDATA_TABLE = 'TraceXYData'
    RESULT_TAGS_TABLE = 'ResultTags'
    PLOT_TAGS_TABLE = 'PlotTags'

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
        self.DB = driver.DriverMySQL(connectionInfo)

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
        
        self.DB.query(q, commit = True)
        self.DB.query("SELECT LAST_INSERT_ID()")
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
        self.DB.query(q)
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
        if self.DB.query(q, commit = True):
            return result
        else:
            return None
    
    def deleteResult(self, resultId):
        '''
        Delete a Result object from the database
        :param resultId: int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = '{1}';".format(self.RESULTS_TABLE, resultId)
        self.DB.query(q, commit = True)

#// Plot create, delete, update, retrieve...

    def createPlot(self, resultId, kind = None):
        '''
        Create a Plot associated with the specified Result:
        :param resultId: int of the Result to associate with the Plot
        :param kind: Plot.KIND* specify what type of plot it is
        :return Plot object if successful, None otherwise.
        '''
        q = "INSERT INTO `{0}` (`fkResults`, `plotKind`) VALUES ({1}, {2});".format(self.PLOTS_TABLE, resultId, kind)
        self.DB.query(q, commit = True)
        self.DB.query("SELECT LAST_INSERT_ID()")
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
        self.DB.query(q)
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.Plot(plotId, row[0], row[1])
        
    def deletePlot(self, plotId):
        '''
        Delete the specified Plot
        :param plotId: int of the plot to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.PLOTS_TABLE, plotId)
        self.DB.query(q, commit = True)

#// Trace create, retrieve, update, delete...

    def createTrace(self, plotId, xyData, name = None, legend = None):
        '''
        Create a trace on the specified Plot
        :param plotId: Plot to which the trace belongs
        :param xyData: float list of tuples (x, y) or (x, y, yError)
        :param name: trace name
        :param legend: trace legend for display
        :return Trace object if successful, None otherwise
        '''
        q = "INSERT INTO `{0}` (`fkPlots`, `name`, `legend`) VALUES ({1}, ".format(self.TRACES_TABLE, plotId)
        q += "'{0}'".format(name) if name else "NULL"
        q += ", "
        q += "'{0}'".format(legend) if legend else "NULL"
        q += ");"
        
        if not self.DB.query(q, commit = False):
            return None
        
        self.DB.query("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        traceId = row[0]
        
        q = "INSERT INTO `{0}` (`fkTraces`, `XValue`, `YValue`, `YErrSize`) VALUES ".format(self.TRACE_XYDATA_TABLE)

        firstTime = True
        for point in xyData:
            if firstTime:
                q += "("
                firstTime = False
            else:
                q += ", ("
            
            q += "{0}, {1}, {2}, {3})".format(
                traceId, 
                point[0], 
                point[1],
                "0" if len(point) < 3 else "{0}".format(point[2]))
            
        q += ";"        
        
        if not self.DB.query(q, commit = True):
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
        self.DB.query(q)
        row = self.DB.fetchone()
        if not row:
            return None
        plotId, name, legend = row[0], row[1], row[2]
        
        q = "SELECT `XValue`, `YValue`, `YErrSize` FROM {0} WHERE `fkTraces` = {1} ORDER BY `keyId`;".format(
            self.TRACE_XYDATA_TABLE, traceId)
        self.DB.query(q)
        result = self.DB.fetchall()
        
        xyData = []
        if result:
            for row in result:
                xyData.append((row[0], row[1], row[2]))
        
        return RI.Trace(traceId, plotId, xyData, name, legend)

    def deleteTrace(self, traceId):
        '''
        Delete the specified trace
        :param traceId int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `fkTraces` = {1};".format(self.TRACE_XYDATA_TABLE, traceId)
        if self.DB.query(q, commit = False):            
        
            q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.TRACES_TABLE, traceId)
            if not self.DB.query(q, commit = True):
                self.DB.rollbackTransaction()
        
#// TagsInterface        
    
    def setResultTags(self, resultId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Result:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param resultId: int of the Result to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        self.__setTags(resultId, self.RESULT_TAGS_TABLE, 'fkResults', tagDictionary)
        
    def getResultTags(self, resultId, tagNames = None):       
        '''
        Retrieve tags on the specified Result:
        :param resultId: int of the Result to query
        :param tagNames: list of strings or None, indicating fetch all tags
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        return self.__getTags(resultId, self.RESULT_TAGS_TABLE, 'fkResults', tagNames)
        
    def setPlotTags(self, plotId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Plot:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param plotId: int of the Plot to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        self.__setTags(plotId, self.PLOT_TAGS_TABLE, 'fkPlots', tagDictionary)
        
    def getPlotTags(self, plotId, tagNames):       
        '''
        Retrieve tags on the specified Plot:
        :param plotId: int of the Plot to query
        :param tagNames: list of strings or None, indicating fetch all tags
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        return self.__getTags(plotId, self.PLOT_TAGS_TABLE, 'fkPlots', tagNames)

#// Database helper and private methods...
            
    def __setTags(self, fkId, targetTable, fkColName, tagDictionary):
        '''
        implement set/update/delete tags
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param fkId:      int id of the parent object the tags reference 
        :param targetTable:   what tags table to update
        :param fkColName:     name of the foreign key column in targetTable
        :param tagDictionary: dictionary of tag names and values.
        '''

        if not fkId:
            raise ValueError('Invalid fkId.')
        
        deleteList = []
        insertList = []
        
        for key, value in tagDictionary.items():
            if key:
                deleteList.append(key)
                if not (value is None or value is False):
                    insertList.append((key, value))
        
        if deleteList:
            q = "DELETE FROM `{0}` WHERE `{1}` = {2} AND (".format(targetTable, fkColName, fkId)
            firstTime = True
            for key in deleteList:
                if firstTime:
                    firstTime = False
                else:
                    q += " OR "
                q += "tagName = '{0}'".format(key)
            q += ");"
            self.DB.query(q, commit = False)
    
        if insertList:
            q = "INSERT INTO `{0}` (`{1}`, `tagName`, `tagValue`) VALUES (".format(targetTable, fkColName)
            firstTime = True
            for item in insertList:
                if firstTime:
                    firstTime = False
                else:
                    q += "), ("
                q += "{0}, '{1}', '{2}'".format(fkId, item[0], item[1])
            q += ");"
            self.DB.query(q, commit = True)
        
    def __getTags(self, fkId, targetTable, fkColName, tagNames):
        '''
        Implement retrieve tag values
        :param fkId: integer id of the time series to query
        :param targetTable:   what tags table to query
        :param fkColName:     name of the foreign key column in targetTable
        :param tagNames: list of strings or None, indicating fetch all tags
        :return dictionary of {tagName, tagValue} where tagValue is None if the tag was not found.  String otherwise.
        '''
        if not fkId:
            raise ValueError('Invalid fkId.')
        
        q = "SELECT tagName, tagValue FROM `{0}` WHERE `{1}` = {2}".format(targetTable, fkColName, fkId)
        
        if tagNames is not None:
            q += " AND ("
            result = {}
            firstTime = True
            for tagName in tagNames:
                result[tagName] = None
                if firstTime:
                    firstTime = False
                else:
                    q += " OR "
                q += "tagName = '{0}'".format(str(tagName))
            q += ");"
        
        self.DB.query(q)        
        records = self.DB.fetchall()
        result = {}
        for tagName, tagValue in records:
            result[tagName] = tagValue
        return result

    def createTables(self):
        self.DB.query("USE {0};".format(self.database))
        
        # Results table
        self.DB.query("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `description` TEXT NULL DEFAULT NULL,
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`)
                ) ENGINE=InnoDB;
            """.format(self.RESULTS_TABLE))

        # Plots table        
        self.DB.query("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `plotKind` TINYINT NOT NULL DEFAULT '0',
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`),
                INDEX `fkResults` (`fkResults`)
                ) ENGINE=InnoDB;
            """.format(self.PLOTS_TABLE))

        # Traces table        
        self.DB.query("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `name` TEXT NULL DEFAULT NULL,
                `legend` TEXT NULL DEFAULT NULL,
                PRIMARY KEY (`keyId`),
                INDEX `fkPlots` (`fkPlots`)
                ) ENGINE=InnoDB;
            """.format(self.TRACES_TABLE))

        # TraceXYData table
        self.DB.query("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkTraces` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `XValue` FLOAT NOT NULL,
                `YValue` FLOAT NOT NULL,
                `YErrSize` FLOAT NOT NULL DEFAULT '0' COMMENT 'error bar size centered on YValue',
                PRIMARY KEY (`keyId`),
                INDEX `fkTraces` (`fkTraces`)
                ) ENGINE=InnoDB;
            """.format(self.TRACE_XYDATA_TABLE))

        # ResultTags table
        self.DB.query("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkResults` (`fkResults`)                
                ) ENGINE=InnoDB;
            """.format(self.RESULT_TAGS_TABLE))

        # PlotTags table        
        self.DB.query("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkPlots` (`fkPlots`)                
                ) ENGINE=InnoDB;
            """.format(self.PLOT_TAGS_TABLE))
        
    def deleteTables(self):
        self.DB.query("USE {0};".format(self.database))
        self.DB.query("DROP TABLE `{0}`".format(self.RESULTS_TABLE))
        self.DB.query("DROP TABLE `{0}`".format(self.PLOTS_TABLE))
        self.DB.query("DROP TABLE `{0}`".format(self.TRACES_TABLE))
        self.DB.query("DROP TABLE `{0}`".format(self.TRACE_XYDATA_TABLE))
        self.DB.query("DROP TABLE `{0}`".format(self.RESULT_TAGS_TABLE))
        self.DB.query("DROP TABLE `{0}`".format(self.PLOT_TAGS_TABLE))

