from EncryptedInMemDb import EncryptedInMemDb
from Fernet import FernetCrypto
import sqlite3

class SqliteDatabase(EncryptedInMemDb):
    '''In-memory SQLite database'''
    
    # NOTE: Not doing work in ctor because that shall not be!
    def __init__(self, connection, crypto):
        self.connection = connection
        self.crypto = crypto
        
    @staticmethod
    def _get_connection():
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        return connection
        
    @staticmethod
    def from_script(script, master_pwd):
        (crypto, salt) = FernetCrypto.from_pwd(master_pwd)
        connection = SqliteDatabase._get_connection()
        db = SqliteDatabase(connection, crypto)
        db.execute_script(script)
        return (db, salt)
    
    @staticmethod
    def from_backup(enc_backup, master_pwd, salt):
        (crypto, _) = FernetCrypto.from_pwd(master_pwd, salt)
        with open(enc_backup, 'rb') as f:
            blob = f.read()
            
        if not (backup := crypto.decrypt(blob)):
            return None
            
        backup = backup.decode("utf-8")
        connection = SqliteDatabase._get_connection()
        db = SqliteDatabase(connection, crypto)
        db.execute_script(backup)
        return db
    
    def execute(self, statement):
        self.connection.cursor().execute(statement)
        
    def execute_script(self, script):
        self.connection.cursor().executescript(script) #Note: Automatically creates transactions
        
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()

    def backup(self, backup_file):
        backup = ""
        for line in self.connection.iterdump():
            backup += '%s\n' % line
            
        bin_backup = backup.encode()
        token = self.crypto.encrypt(bin_backup)
    
        with open(backup_file, 'wb') as f:
            f.write(token)

    def close(self):
        self.connection.close()