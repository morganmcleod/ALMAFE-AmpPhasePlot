'''
Database for storage and retrieval of plot image files
'''
import Database.Interface.PlotImage as PI
import Database.Driver.MySQL as driver

class PlotImageDatabase(PI.PlotImageInterface):
    '''
    Database for storage and retrieval of plot image files
    '''
    PLOTS_TABLE = 'Plots'
    PLOT_IMAGES_TABLE = 'PlotImages'

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
        self.createTables()
        
    def createPlotImage(self, plotId, imageData, name = None, path = None):
        '''
        Create a new PlotImage object in the database
        :param plotId:    Plot object to assocate this image with
        :param imageData: Binary image data
        :param name: str  
        :param path: str may be used for filesystem storage
        :return PlotImage object if successful, None otherwise
        '''
        q = "INSERT INTO `{0}` (`fkPlots`, `name`, `path`, `imageData`) VALUES (%s, %s, %s, %s);".format(self.PLOT_IMAGES_TABLE)
        
        name = "'{0}'".format(name) if name else "NULL"
        path = "'{0}'".format(path) if path else "NULL"  
        
        params = (plotId, name, path, imageData)
        if not self.DB.execute(q, params):
            return None
        
        self.DB.execute("SELECT LAST_INSERT_ID()")
        row = self.DB.fetchone()
        if not row:
            return None
        
        self.DB.commit()
        return PI.PlotImage(plotId, row[0], imageData, name, path)
        
    
    def retrievePlotImage(self, plotImageId):
        '''
        Retrieve the specified PlotImage object from the database
        :param plotImageId: to retrieve
        :return PlotImage object if successful, None otherwise
        '''
        q = "SELECT `fkPlots`, `name`, `path`, `imageData` FROM {0} WHERE `keyId` = {1};".format(self.PLOT_IMAGES_TABLE, plotImageId)
        self.DB.execute(q)
        row = self.DB.fetchone()
        if not row:
            return None
        name = row[1]
        if name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        path = row[2]
        if path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
        return PI.PlotImage(row[0], plotImageId, row[3], name, path)

    def deletePlotImage(self, plotImageId):
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
                `fkPlots` INT(10) UNSIGNED NOT NULL DEFAULT '0',
                `name` TEXT NULL DEFAULT NULL,
                `path` TEXT NULL DEFAULT NULL,                
                `timeStamp` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                `imageData` MEDIUMBLOB NULL,
                PRIMARY KEY (`keyId`),
                FOREIGN KEY (`fkPlots`) REFERENCES {1}(`keyId`) ON DELETE CASCADE                
                ) ENGINE=InnoDB;
            """.format(self.PLOT_IMAGES_TABLE, self.PLOTS_TABLE))
     
    def deleteTables(self):
        self.DB.execute("USE {0};".format(self.database))
        self.DB.execute("DROP TABLE `{0}`".format(self.PLOT_IMAGES_TABLE))   
        