'''
Database for storage and retrieval of plot image files
'''
import ALMAFE.database.DriverMySQL as driver
from Database.Interface.PlotImage import *
from Utility.StripQuotes import stripQuotes

class PlotImageDatabase(PlotImageInterface):
    '''
    Database for storage and retrieval of plot image files
    '''
    PLOT_IMAGES_TABLE = 'AmpPhase_PlotImages'

    def __init__(self, PLOT_RESULTS_TABLE, user, passwd = None, host = '127.0.0.1', database = 'AmpPhaseData', use_pure = False): 
        '''
        Constructor
        '''
        self.PLOT_RESULTS_TABLE = PLOT_RESULTS_TABLE
        connectionInfo = {
            'user' : user,
            'passwd' : passwd,
            'host' : host,
            'database' : database,
            'use_pure' : use_pure            
        }
        self.database = database
        self.DB = driver.DriverMySQL(connectionInfo)
        self.createTables()
        
    def create(self, plotResultId, imageData, name = None, kind = None, path = None):
        '''
        Create a new PlotImage object in the database
        :param plotResultId: PlotResult object to associate this image with
        :param imageData: Binary image data
        :param name: str  
        :param kind: int
        :param path: str may be used for filesystem storage
        :return PlotImage object if successful, None otherwise
        '''
        q = "INSERT INTO `{0}` (`fkPlotResults`, `name`, `kind`, `path`, `imageData`) VALUES (%s, %s, %s, %s, _binary %s);".format(self.PLOT_IMAGES_TABLE)
        
        name = name if name else "NULL"
        kind = kind if kind else 0
        path = path if path else "NULL"  
        
        params = (plotResultId, name, kind, path, imageData)
        if not self.DB.execute(q, params):
            return None
        
        self.DB.execute("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        
        self.DB.commit()
        return PlotImage(plotResultId, row[0], imageData, name, kind, path)
        
    
    def retrieve(self, plotImageId, plotResultId = None):
        '''
        Retrieve the specified PlotImage object from the database
        :param plotImageId: to retrieve
        :param plotResultId: if provided, retrieve all PlotImages associated with the specified Id.
        :return PlotImage object if successful, None otherwise
        '''
        q = "SELECT `fkPlotResults`, `name`, `kind`, `path`, `imageData` FROM {0} ".format(self.PLOT_IMAGES_TABLE)
        if plotResultId:
            q += "WHERE fkPlotResults = {0};".format(plotResultId)
        else:
            q += "WHERE `keyId` = {0};".format(plotImageId)
        
        self.DB.execute(q)
        rows = self.DB.fetchall()
        if not rows:
            return None
        if plotResultId:            
            return [PlotImage(
                plotImageId = plotImageId,
                plotResultId = row[0],
                name = stripQuotes(row[1]),
                kind = row[2],
                path = stripQuotes(row[3]),
                imageData = row[4]                        
            ) for row in rows]
        else:
            row = rows[0]
            return PlotImage(
                plotImageId = plotImageId,
                plotResultId = row[0],
                name = stripQuotes(row[1]),
                kind = row[2],
                path = stripQuotes(row[3]),
                imageData = row[4]                        
            )

    def delete(self, plotImageId):
        '''
        Delete the specified PlotImage object from the database
        :param plotImageId: to delete
        '''
        q = "DELETE FROM `{0}` WHERE `keyId` = {1};".format(self.PLOT_IMAGES_TABLE, plotImageId)
        self.DB.execute(q, commit = True)
        
    def createTables(self):
        self.DB.execute("USE {0};".format(self.database))
        
        # PlotImages table
        self.DB.execute("""
                CREATE TABLE IF NOT EXISTS `{0}` (
                `keyId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
                `fkPlotResults` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `name` TEXT NULL DEFAULT NULL,
                `kind` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `path` TEXT NULL DEFAULT NULL,                
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                `imageData` MEDIUMBLOB NULL,
                PRIMARY KEY (`keyId`),
                FOREIGN KEY (`fkPlotResults`) REFERENCES {1}(`keyId`) ON DELETE CASCADE                
                ) ENGINE=InnoDB;
            """.format(self.PLOT_IMAGES_TABLE, self.PLOT_RESULTS_TABLE))
     
    def deleteTables(self):
        self.DB.execute("USE {0};".format(self.database))
        self.DB.execute("DROP TABLE `{0}`".format(self.PLOT_IMAGES_TABLE))   
        