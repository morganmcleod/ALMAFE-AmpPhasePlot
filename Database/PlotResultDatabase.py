import ALMAFE.database.DriverMySQL as driver
import Database.Interface.PlotResult as RI
import Database.Interface.Tags as TI
import Database.TagsDatabase as TagsDB
from AmpPhaseDataLib.Constants import PlotKind
from itertools import zip_longest

class PlotResultDatabase(RI.PlotResultInterface, TI.TagsInterface):
    '''
    MySQL implementation of Database.Interface.PlotResult.ResultInterface
    '''
    PLOT_RESULTS_TABLE = 'AmpPhase_Results'
    PLOT_RESULT_TAGS_TABLE = 'AmpPhase_ResultTags'

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

# ResultInterface create, retrieve, update, delete...

    def create(self, description = None, timeStamp = None):
        '''
        Create a new PlotResult object in the database
        :param description: str
        :param timeStamp: datetime to associate with the PlotResult.  Defaults to now(). 
        :return PlotResult object if succesful, None otherwise.
        '''
        q = "INSERT INTO `{0}` (`description`".format(self.PLOT_RESULTS_TABLE)
        if (timeStamp):
            q += ", `timeStamp`"
        q += ") VALUES ("
        q += "'{0}'".format(description) if description else "NULL"
        if (timeStamp):
            q += ", '{0}'".format(timeStamp.strftime(self.DB.TIMESTAMP_FORMAT))
        q += ");"
        
        self.DB.execute(q, commit = True)
        self.DB.execute("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.PlotResult(row[0], description, timeStamp)
    
    def retrieve(self, plotResultId):
        '''
        Retrieve a PlotResult object from the database
        :param plotResultId: int to retrieve
        :return PlotResult object if succesful, None otherwise.
        '''
        q = "SELECT `description`, `timeStamp` FROM `{0}` WHERE `keyId` = '{1}';".format(self.PLOT_RESULTS_TABLE, plotResultId)
        self.DB.execute(q)
        row = self.DB.fetchone()
        if not row:
            return None
        return RI.PlotResult(plotResultId, row[0], row[1])

    def update(self, result):
        '''
        Update an existing PlotResult object in the database
        :param PlotResult: object to update
        :return PlotResult object if successful, None otherwise.
        '''
        q = "UPDATE `{0}` SET `Description` = '{1}'".format(self.PLOT_RESULTS_TABLE, result.description)
        if result.timeStamp:
            q += ", `timeStamp` = '{0}'".format(result.timeStamp.strftime(self.DB.TIMESTAMP_FORMAT))
        q += " WHERE `keyId` = '{0}';".format(result.plotResultId)
        if self.DB.execute(q, commit = True):
            return result
        else:
            return None
    
    def delete(self, plotResultId):
        '''
        Delete a PlotResult object from the database
        Underlying Plots, PlotImages, Traces, and Tags are deleted via ON DELETE CASCADE
        :param plotResultId: int to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = '{1}';".format(self.PLOT_RESULTS_TABLE, plotResultId)
        self.DB.execute(q, commit = True)

    def setTags(self, plotResultId, tagDictionary):
        '''
        Set, update, or delete tags on the specified PlotResult:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param plotResultId: int of the PlotResult to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        self.tagsDB.setTags(plotResultId, self.PLOT_RESULT_TAGS_TABLE, 'fkPlotResults', tagDictionary)
        
    def getTags(self, plotResultId, tagNames = None):       
        '''
        Retrieve tags on the specified PlotResult:
        :param plotResultId: int of the PlotResult to query
        :param tagNames: list of strings or None, indicating fetch all tags
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        return self.tagsDB.getTags(plotResultId, self.PLOT_RESULT_TAGS_TABLE, 'fkPlotResults', tagNames)

# Database helper and private methods...
    
    def createTables(self):
        self.DB.execute("USE {0};".format(self.database))
        
        # PlotResults table
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `description` TEXT NULL DEFAULT NULL,
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`keyId`)
                ) ENGINE=InnoDB;
            """.format(self.PLOT_RESULTS_TABLE))

        # PlotResult Tags table
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `fkPlotResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `tagName` TINYTEXT NOT NULL,
                `tagValue` TEXT NOT NULL,
                INDEX `fkPlotResults` (`fkPlotResults`),
                FOREIGN KEY (`fkPlotResults`) REFERENCES {1}(`keyId`) ON DELETE CASCADE
                ) ENGINE=InnoDB;
            """.format(self.PLOT_RESULT_TAGS_TABLE, self.PLOT_RESULTS_TABLE))
        
    def deleteTables(self):
        self.DB.execute("USE {0};".format(self.database))
        self.DB.execute("DROP TABLE `{0}`".format(self.PLOT_RESULT_TAGS_TABLE))
        self.DB.execute("DROP TABLE `{0}`".format(self.PLOT_RESULTS_TABLE))
