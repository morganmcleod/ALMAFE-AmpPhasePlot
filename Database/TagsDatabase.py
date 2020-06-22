'''
Implement set/get tags in a database driver neutral way.
This is used by TimeSeriesDatabase with SQLite and by ResultsDatabase with MySQL.
'''

class TagsDatabase(object):
    '''
    Implement get/set tags in a database driver neutral way.
    '''

    def __init__(self, driver):
        '''
        Constructor
        '''
        self.driver = driver
        
    def setTags(self, fkId, targetTable, fkColName, tagDictionary):
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
            self.driver.query(q, commit = False)
    
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
            self.driver.query(q, commit = True)
        
    def getTags(self, fkId, targetTable, fkColName, tagNames):
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
        
        self.driver.query(q)        
        records = self.driver.fetchall()
        result = {}
        for tagName, tagValue in records:
            result[tagName] = tagValue
        return result
    