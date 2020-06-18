'''
Driver wrapper for mysql-connector-python
'''
import mysql.connector
from mysql.connector import Error

class DriverMySQL():
    '''
    Driver wrapper for mysql-connector-python
    Provides a uniform interface to SQL user code
    '''

    def __init__(self, connectionInfo):
        '''
        Constructor
        :param connectionInfo: dictionary having the items needed to connect to MySQL server
        '''
        self.host = connectionInfo['host']
        self.user = connectionInfo['user']
        self.passwd = connectionInfo['passwd']
        self.database = connectionInfo['database']        
        self.port = connectionInfo.get('port', 3306)
        self.cursor = None
        if self.connect():
            self.cursor = self.connection.cursor()
        
    def connect(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, database=self.database)
            return True
        except Error as e:
            print(f"MySQL error: {e}")
            return False

    def disconnect(self):
        try:
            self.connection.close()
            self.connection = None
            self.cursor = None
            return True
        except Error as e:
            print(f"MySQL error: {e}")
            return False
        
    def query(self, query, commit = False):
        try:
            self.cursor.execute(query)
            if commit:
                self.connection.commit()
            return True
        except Error as e:
            print(f"MySQL error: {e}")
            print(query)
            return False
    
    def commit(self):
        try:
            self.connection.commit()
            return True
        except Error as e:
            print(f"MySQL error: {e}")
            return False
        
    def rollback(self):
        try:
            self.connection.rollback()
            return True
        except Error as e:
            print(f"MySQL error: {e}")
            return False

    def fetchone(self):
        try:
            row = self.cursor.fetchone()
            return row
        except Error as e:
            print(f"MySQL error: {e}")
            return False    

    def fetchmany(self, chunkSize):
        try:
            result = self.cursor.fetchmany(chunkSize)
            return result
        except Error as e:
            print(f"MySQL error: {e}")
            return False
        
    def fetchall(self):
        try:
            result = self.cursor.fetchall()
            return result
        except Error as e:
            print(f"MySQL error: {e}")
            return False


