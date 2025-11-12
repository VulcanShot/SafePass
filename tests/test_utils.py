import os
import safepass.safepass as safepass

def get_test_db_file(name):
    abspath = os.path.abspath(__file__)
    dir = os.path.dirname(abspath)
    return os.path.join(dir, 'db', name)

RAISER_EXCEPTION = 'ALERT'

GOOD_DB_FILE = get_test_db_file('safepass.db.enc')
GOOD_SALT_FILE = get_test_db_file('safepass.salt.bin')

BAD_DB_FILE = get_test_db_file('bad.db.enc')
BAD_SALT_FILE = get_test_db_file('bad.salt.bin')

TEST_DB_FILE = get_test_db_file('temp.db.enc')
TEST_SALT_FILE = get_test_db_file('temp.bin')
TEST_PASSWORD = 'pcs is the best first year module'

def raiser():
    raise RuntimeError(RAISER_EXCEPTION)

def popper(ls):
    def pop(_):
        return ls.pop(0)
    return pop

def mock_input(monkeypatch, obj, input_list):
    monkeypatch.setattr(obj, 'getpass', popper(input_list))
    monkeypatch.setattr('builtins.input', popper(input_list))
    
def new_mock_db(monkeypatch):
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    if os.path.exists(TEST_SALT_FILE):
        os.remove(TEST_SALT_FILE)
    monkeypatch.setattr(safepass, 'ENCRYPTED_DB_FILE', get_test_db_file(TEST_DB_FILE))
    monkeypatch.setattr(safepass, 'SALT_FILE', get_test_db_file(TEST_SALT_FILE))