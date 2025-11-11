import test_utils

import SqlStatements
from SqliteDatabase import SqliteDatabase

test_password = 'pcs is the best first year module'

def test_new_database():
    (db, _) = SqliteDatabase.from_script(SqlStatements.CREATE_TABLES, test_password)
    db.execute("INSERT INTO Service (Name, Url) VALUES ('Netflix', NULL)")
    res = db.execute("SELECT Name, Url FROM Service")
    assert res.fetchone()['Name'] == 'Netflix'

def test_from_backup(db_file=test_utils.GOOD_DB_FILE, _salt_file=test_utils.GOOD_SALT_FILE):
    db = SqliteDatabase.from_backup(db_file, _salt_file, test_password)
    assert db
    res = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Service'")
    assert res.fetchone() is not None
    res = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Account'")
    assert res.fetchone() is not None

def test_backup():
    (db, salt) = SqliteDatabase.from_script(SqlStatements.CREATE_TABLES, test_password)
    
    with open(test_utils.TEST_SALT_FILE, 'wb') as f:
        f.write(salt)
    
    db.backup(test_utils.TEST_BACKUP_FILE)
    test_from_backup(test_utils.TEST_BACKUP_FILE, test_utils.TEST_SALT_FILE)
    
def test_from_backup_corrupted_db():
    db = SqliteDatabase.from_backup(test_utils.BAD_DB_FILE, test_utils.GOOD_SALT_FILE, test_password)
    assert not db
    
def test_from_backup_bad_salt():
    db = SqliteDatabase.from_backup(test_utils.GOOD_DB_FILE, test_utils.BAD_SALT_FILE, test_password)
    assert not db