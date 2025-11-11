import os

def get_test_db_file(name):
    abspath = os.path.abspath(__file__)
    dir = os.path.dirname(abspath)
    return os.path.join(dir, 'db', name)

RAISER_EXCEPTION = 'ALERT'

GOOD_DB_FILE = get_test_db_file('safepass.db.enc')
GOOD_SALT_FILE = get_test_db_file('safepass.salt.bin')

BAD_DB_FILE = get_test_db_file('bad.db.enc')
BAD_SALT_FILE = get_test_db_file('bad.salt.bin')

TEST_BACKUP_FILE = get_test_db_file('temp.db.enc')
TEST_SALT_FILE = get_test_db_file('temp.bin')

def raiser():
    raise RuntimeError(RAISER_EXCEPTION)

def popper(ls):
    def pop(_):
        return ls.pop(0)
    return pop