from InMemoryDatabase import InMemoryDatabase
import sqlite3

class SqliteDatabase(InMemoryDatabase):
    '''In-memory SQLite database'''
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    @staticmethod
    def open():
        #NOTE: Not doing work in ctor because that shall not be!
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        return (con, cur)
    
    def load_dump(self, dump):
        with open(dump, 'r') as f:
            for line in f:
                self.execute(line)
    
    def execute(self, statement):
        self.cursor.execute(statement)
        
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()