import Database.Interface.Result as RI
import mysql.connector
from mysql.connector import Error

class ResultSQL(): # RI.ResultInterface):
    '''
    classdocs
    '''

    def __init__(self, user, passwd = None, host = '127.0.0.1', database = 'AmpPhaseData'): 
        '''
        Constructor
        '''
        self.user = user
        self.passwd = passwd
        self.host = host
        self.database = database
        self.connect()    

    def __del__(self):
        self.connection.close()
        
    def connect(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(host=self.host, user=self.user, passwd=self.passwd, database=self.database)
            return True
        except Error as e:
            print(f"The error '{e}' occurred")
            return False

    def createResult(self, description = None, timeStamp = None):
        '''
        Create a new Result object in the database
        :param description: str
        :param timeStamp: datetime to associate with the Result.  Defaults to now(). 
        :return Result object if succesful, None otherwise.
        '''
        q = "INSERT INTO `Results` (`description`"
        if (timeStamp):
            q += ", `timeStamp`"
        q += ") VALUES ("
        q += "'{0}'".format(description) if description else "NULL"
        if (timeStamp):
            q += ", '{0}'".format(timeStamp)
        q += ");"
        
        self.__executeQuery(q)
        r = self.__executeReadQuery("SELECT LAST_INSERT_ID()")
        if (r):
            return RI.Result(r[0], description, timeStamp)
        else:
            return None

    
    def retrieveResult(self, resultId):
        '''
        Retrieve a Result object from the database
        :param resultId: int to retrieve
        :return Result object if succesful, None otherwise.
        '''
        q = "SELECT `description`, `timeStamp` FROM `Results` WHERE `keyId` = '{0}';".format(resultId)
        r = self.__executeReadQuery(q)
        if (r):
            return RI.Result(resultId, r[0][0], r[0][1])
        else:
            return None


    def createTables(self):
        self.__executeQuery("USE {0};".format(self.database))
        
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `Results` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `description` TEXT NULL DEFAULT NULL,
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`)
                ) ENGINE=InnoDB;
            """)
        
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `Plots` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `plotType` TINYINT NOT NULL DEFAULT '0',
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`),
                INDEX `fkResults` (`fkResults`)
                ) ENGINE=InnoDB;
            """)
        
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `Traces` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `legend` TEXT NULL DEFAULT NULL,
                PRIMARY KEY (`keyId`),
                INDEX `fkPlots` (`fkPlots`)
                ) ENGINE=InnoDB;
            """)

        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `TraceXYData` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkTraces` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `XValue` FLOAT,
                `YValue` FLOAT,
                `YErrSize` FLOAT DEFAULT '0' COMMENT 'error bar size centered on YValue',
                PRIMARY KEY (`keyId`),
                INDEX `fkTraces` (`fkTraces`)
                ) ENGINE=InnoDB;
            """)

        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `ResultTags` (
                `fkResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkResults` (`fkResults`)                
                ) ENGINE=InnoDB;
            """)
        
        self.__executeQuery("""
                CREATE TABLE IF NOT EXISTS `PlotTags` (
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkPlots` (`fkPlots`)                
                ) ENGINE=InnoDB;
            """)
        
    def deleteTables(self):
        self.__executeQuery("USE {0};".format(self.database))
        self.__executeQuery("DROP TABLE `Results`")
        self.__executeQuery("DROP TABLE `Plots`")
        self.__executeQuery("DROP TABLE `Traces`")
        self.__executeQuery("DROP TABLE `TraceXYData`")
        self.__executeQuery("DROP TABLE `ResultTags`")
        self.__executeQuery("DROP TABLE `PlotTags`")
        
    def __executeQuery(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
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
        
        
        
        
        

