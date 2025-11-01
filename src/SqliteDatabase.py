from InMemoryDatabase import InMemoryDatabase
import sqlite3

class SqliteDatabase(InMemoryDatabase):
    '''In-memory SQLite database'''
    
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor
        
    @staticmethod
    def open(script = None):
        #NOTE: Not doing work in ctor because that shall not be!
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        db = SqliteDatabase(con, cur)
        db.execute_script(script)
        return db
    
    def execute(self, statement):
        self.cursor.execute(statement)
        
    def execute_script(self, script):
        self.cursor.executescript(script) #Note: Automatically creates transactions
        
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()

    def backup(self):
        backup = ""
        for line in self.connection.iterdump():
            backup += '%s\n' % line
        return backup

    def close(self):
        self.connection.close()