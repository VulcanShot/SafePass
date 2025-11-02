from EncryptedInMemDb import EncryptedInMemDb
from FernetCrypto import FernetCrypto
import sqlite3

class SqliteDatabase(EncryptedInMemDb):
    '''In-memory SQLite database'''
    
    # NOTE: Not doing work in ctor because that shall not be!
    def __init__(self, connection, _crypto):
        self.connection = connection
        self.crypto = _crypto
        
    @staticmethod
    def _get_connection() -> sqlite3.Connection:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.autocommit = True #Note: Automatically creates transactions (https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.autocommit)
        return connection
        
    @staticmethod
    def from_script(script: str, master_pwd: str):
        '''Factory method'''
        (crypto, salt) = FernetCrypto.from_pwd(master_pwd)
        db = SqliteDatabase(SqliteDatabase._get_connection(), crypto)
        db.execute_script(script)
        return (db, salt)
    
    @staticmethod
    def from_backup(backup_file: str, salt_file: str, master_pwd: str):
        '''Factory method'''
        with open(salt_file, 'rb') as f:
            salt = f.read()
            
        crypto = FernetCrypto.from_pwd(master_pwd, salt)
        with open(backup_file, 'rb') as f:
            blob = f.read()
            
        if not (backup := crypto.decrypt_to_str(blob)):
            return None
            
        db = SqliteDatabase(SqliteDatabase._get_connection(), crypto)
        db.execute_script(backup)
        return db
    
    def execute(self, statement: str) -> sqlite3.Cursor:
        cur = self.connection.cursor().execute(statement)
        return cur
        
    def execute_script(self, script: str) -> sqlite3.Cursor:
        cur = self.connection.cursor().executescript(script)
        return cur

    def backup(self, file: str) -> None:
        backup = ""
        for line in self.connection.iterdump():
            backup += '%s\n' % line
            
        token = self.crypto.encrypt(backup)
    
        with open(file, 'wb') as f:
            f.write(token)

    def close(self) -> None:
        self.connection.close()