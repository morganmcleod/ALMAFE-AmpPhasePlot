import Database.Interface.Result as RI
import Database.Interface.Tag as TI
import mysql.connector
from mysql.connector import Error

class ResultMySQL(RI.ResultInterface):
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
        self.user = user
        self.passwd = passwd
        self.host = host
        self.database = database
        self.connect()    
        
    def connect(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(host=self.host, user=self.user, passwd=self.passwd, database=self.database)
            return True
        except Error as e:
            print(f"The error '{e}' occurred")
            return False

#// Result methods

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
        
        self.__executeQuery(q)
        r = self.__executeReadQuery("SELECT LAST_INSERT_ID()")
        if not r:
            return None
        return RI.Result(r[0], description, timeStamp)
            
    
    def retrieveResult(self, resultId):
        '''
        Retrieve a Result object from the database
        :param resultId: int to retrieve
        :return Result object if succesful, None otherwise.
        '''
        q = "SELECT `description`, `timeStamp` FROM `{0}` WHERE `keyId` = '{1}';".format(self.RESULTS_TABLE, resultId)
        r = self.__executeReadQuery(q)
        if not r:
            return None
        row = r[0]
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
        if self.__executeQuery(q):
            return result
        else:
            return None
    
    def deleteResult(self, resultId):
        '''
        Delete a Result object from the database
        :param resultId: int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = '{1}';".format(self.RESULTS_TABLE, resultId)
        self.__executeQuery(q)

#// Plot methods

    def createPlot(self, resultId, kind = None):
        '''
        Create a Plot associated with the specified Result:
        :param resultId: int of the Result to associate with the Plot
        :param kind: Plot.KIND* specify what type of plot it is
        :return Plot object if successful, None otherwise.
        '''
        q = "INSERT INTO `{0}` (`fkResults`, `plotKind`) VALUES ({1}, {2});".format(self.PLOTS_TABLE, resultId, kind)
        self.__executeQuery(q)
        r = self.__executeReadQuery("SELECT LAST_INSERT_ID()")
        if not r:
            return None
        return RI.Plot(r[0], resultId, kind)
    
    def retrievePlot(self, plotId):
        '''
        Retrieve a specified Plot:
        :param plotId: int of the plot to retrieve
        :return Plot object if successful, None otherwise.
        '''
        q = "SELECT `fkResults`, `plotKind` FROM `{0}` WHERE `keyId` = {1};".format(self.PLOTS_TABLE, plotId)
        r = self.__executeReadQuery(q)
        if not r:
            return None
        row = r[0]
        return RI.Plot(plotId, row[0], row[1])
        
    def deletePlot(self, plotId):
        '''
        Delete the specified Plot
        :param plotId: int of the plot to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.PLOTS_TABLE, plotId)
        self.__executeQuery(q)

#// Trace methods

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
        self.__executeQuery(q, commit = False)
        r = self.__executeReadQuery("SELECT LAST_INSERT_ID()")
        if not r:
            return None
        traceId = r[0]
        
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
                "NULL" if len(point) < 3 else "{0}".format(point[2]))
            
        q += ";"        
        self.__executeQuery(q, commit = True)
        return RI.Trace(traceId, plotId, xyData, name, legend)
    
    def retrieveTrace(self, traceId):
        '''
        Retrieve the specified trace
        :param traceId int to retrieve
        :return Trace object if successful, None otherwise
        '''
        q = "SELECT `fkPlots`, `name`, `legend` FROM {0} WHERE `keyId` = {1};".format(self.TRACES_TABLE, traceId)
        r = self.__executeReadQuery(q)
        if not r:
            return None
        
        row = r[0]
        plotId, name, legend = row[0], row[1], row[2]
        
        q = "SELECT `XValue`, `YValue`, `YErrSize` FROM {0} WHERE `fkTraces` = {1} ORDER BY `keyId`;".format(
            self.TRACE_XYDATA_TABLE, traceId)
        r = self.__executeReadQuery(q)

        xyData = []
        if r:
            for row in r:
                xyData.append((row[0], row[1], row[2]))
        
        return RI.Trace(traceId, plotId, xyData, name, legend)

    def deleteTrace(self, traceId):
        '''
        Delete the specified trace
        :param traceId int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `fkTrace` = {1};".format(self.TRACE_XYDATA_TABLE, traceId)
        self.__executeQuery(q)
        
        q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.TRACES_TABLE, traceId)
        self.__executeQuery(q)
        
                
#// Database helper and private methods

    def createTables(self):
        self.__executeQuery("USE {0};".format(self.database))
        
        # Results table
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `description` TEXT NULL DEFAULT NULL,
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`)
                ) ENGINE=InnoDB;
            """.format(self.RESULTS_TABLE))

        # Plots table        
        self.__executeQuery("""
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
        self.__executeQuery("""
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
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkTraces` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `XValue` FLOAT,
                `YValue` FLOAT,
                `YErrSize` FLOAT DEFAULT '0' COMMENT 'error bar size centered on YValue',
                PRIMARY KEY (`keyId`),
                INDEX `fkTraces` (`fkTraces`)
                ) ENGINE=InnoDB;
            """.format(self.TRACE_XYDATA_TABLE))

        # ResultTags table
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkResults` (`fkResults`)                
                ) ENGINE=InnoDB;
            """.format(self.RESULT_TAGS_TABLE))

        # PlotTags table        
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkPlots` (`fkPlots`)                
                ) ENGINE=InnoDB;
            """.format(self.PLOT_TAGS_TABLE))
        
    def deleteTables(self):
        self.__executeQuery("USE {0};".format(self.database))
        self.__executeQuery("DROP TABLE `{0}`".format(self.RESULTS_TABLE))
        self.__executeQuery("DROP TABLE `{0}`".format(self.PLOTS_TABLE))
        self.__executeQuery("DROP TABLE `{0}`".format(self.TRACES_TABLE))
        self.__executeQuery("DROP TABLE `{0}`".format(self.TRACE_XYDATA_TABLE))
        self.__executeQuery("DROP TABLE `{0}`".format(self.RESULT_TAGS_TABLE))
        self.__executeQuery("DROP TABLE `{0}`".format(self.PLOT_TAGS_TABLE))
        
    def __executeQuery(self, query, commit = True):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            if commit:
                self.connection.commit()
            return True
        except Error as e:
            print(f"The error '{e}' occurred")
            return False
    
    def __commitTransaction(self):
        try:
            self.connection.commit()
            return True
        except Error as e:
            print(f"The error '{e}' occurred")
            return False
    
    def __executeReadQuery(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
            return False
