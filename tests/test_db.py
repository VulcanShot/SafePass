import pytest

from SqliteDatabase import SqliteDatabase
import SqlStatement

import os

DB_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db')
ENCRYPTED_DB_FILE = os.path.join(DB_DIR, 'safepass.db.enc')
SALT_FILE = os.path.join(DB_DIR, 'salt.bin')
TEST_BACKUP_FILE = os.path.join(DB_DIR, 'test.db.enc')
TEST_SALT_FILE = os.path.join(DB_DIR, 'test.bin')

test_password = 'pcs is the best first year module'

def test_new_database():
    (db, _) = SqliteDatabase.from_script(SqlStatement.CREATE_TABLES, test_password)
    db.execute("INSERT INTO Service (Name, Domain) VALUES ('Netflix', NULL)")
    res = db.execute("SELECT Name, Domain FROM Service")
    assert res.fetchone() is not None

def test_from_backup(db_file=ENCRYPTED_DB_FILE, _salt_file=SALT_FILE):
    db = SqliteDatabase.from_backup(db_file, _salt_file, test_password)
    assert db
    res = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Service'")
    assert res.fetchone() is not None

def test_backup():
    (db, salt) = SqliteDatabase.from_script(SqlStatement.CREATE_TABLES, test_password)
    
    with open(TEST_SALT_FILE, 'wb') as f:
        f.write(salt)
    
    db.backup(TEST_BACKUP_FILE)
    test_from_backup(TEST_BACKUP_FILE, TEST_SALT_FILE)