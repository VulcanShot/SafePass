from .EncryptedInMemDb import EncryptedInMemDb
from .FernetCrypto import FernetCrypto
import sqlite3

class SqliteDatabase(EncryptedInMemDb):
    '''In-memory SQLite database'''
    
    # Not doing work in ctor because that shall not be!
    def __init__(self, connection, _crypto):
        self.connection = connection
        self.crypto = _crypto
        
    @staticmethod
    def _get_connection() -> sqlite3.Connection:
        '''Meant for internal use to create the database in memory'''
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.autocommit = True # Automatically creates transactions (https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.autocommit)
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
    
    def change_master_pwd(self, backup_file: str, new_master_pwd: str) -> bytes:
        (crypto, salt) = FernetCrypto.from_pwd(new_master_pwd)
        self.crypto = crypto
        self.backup(backup_file)
        return salt
    
    def execute(self, statement: str, params: dict = ()) -> sqlite3.Cursor:
        try:
            cur = self.connection.cursor().execute(statement, params)
        except sqlite3.IntegrityError():
            cur = None
        return cur
        
    def execute_script(self, script: str) -> sqlite3.Cursor:
        try:
            cur = self.connection.cursor().executescript(script)
        except sqlite3.IntegrityError():
            cur = None
        return cur

    def backup(self, filename: str) -> None:
        backup = ""
        for line in self.connection.iterdump():
            backup += '%s\n' % line
            
        token = self.crypto.encrypt(backup)
    
        with open(filename, 'wb') as f:
            f.write(token)

    def close(self) -> None:
        self.connection.close()