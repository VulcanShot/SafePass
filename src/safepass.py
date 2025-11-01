import os
import logging
from getpass import getpass
import mmap

from SqliteDatabase import SqliteDatabase
from Fernet import FernetCrypto
from SqlStatement import SqlStatement

ENCRYPTED_DB_FILE = os.path.join('db', 'safepass.db.enc')
SALT_FILE = os.path.join('db', 'salt.bin')

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format=f'[{os.path.basename(__file__)}] (%(levelname)s) %(message)s',
    level=logging.DEBUG
)

def change_working_dir():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

def new_master_password():
    #NOTE: NIST https://pages.nist.gov/800-63-4/sp800-63b/passwords/
    # Can't apply rate limiting
    
    while True:
        pwd = getpass('Please create a master password: ')
        if len(pwd) < 15:
            print('Entered password must be at least 15 characters long')
            continue
        with open(os.path.join('res', '100k-most-used-passwords-NCSC.txt'), 'rb') as file, \
            mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s: # NOTE: Explain why mmap (https://stackoverflow.com/a/4944929)
            if s.find(pwd.encode()) != -1:
                print('Entered password has been breached before')
                continue
        break

    # TODO: Confirm password
    return pwd
        
  
def get_salt():
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    return None
        
def write_salt(salt: bytes):
    with open(SALT_FILE, 'wb') as f:
        return f.write(salt)
        
def load_database(crypto: FernetCrypto):
    with open(ENCRYPTED_DB_FILE, 'rb') as f:
        blob = f.read()
        
    if not (dump := crypto.decrypt(blob)):
        LOGGER.error('Wrong password, or the database has been tampered with. Restore a backup or create a new database.')
        # TODO: Give options
        exit(5) #NOTE: Correct return codes
        
    dump = dump.decode("utf-8")
    db = SqliteDatabase.open(dump)
    return db

def create_database(crypto):
    db = SqliteDatabase.open(SqlStatement.CREATE_TABLES)
    
    with open(ENCRYPTED_DB_FILE, 'wb') as f:
        backup = db.backup()
        backup_b = backup.encode()
        token = crypto.encrypt(backup_b)
        f.write(token)
            
    return db

def main_loop(db):
    print('Please select the action you want to take:')
    print('[1] Add new password entry')
    print('[2] Get my password')
    exit(0)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    change_working_dir()
    print('Welcome to SafePass')
    
    if not os.path.exists(ENCRYPTED_DB_FILE): #NOTE: If there is salt but no db, salt is ignored: security
        master_pwd = new_master_password()
        # TODO: Add password requirements
        (crypto, salt) = FernetCrypto.from_pwd(master_pwd)
        write_salt(salt)
        db = create_database(crypto)
        LOGGER.info('Encrypted database and salt files created. We recommend that you back them up.')
        main_loop(db)

    salt_from_file = get_salt()
    if not salt_from_file:
        LOGGER.error(f'The salt file ({SALT_FILE}) has not been found. Please restore it or create a new database.')
        # TODO: Give user options
        exit(2)

    master_pwd = getpass('Please enter your master password: ') #NOTE: Getpass instead of input
    crypto = FernetCrypto.from_pwd(master_pwd, salt_from_file)
    db = load_database(crypto)
    main_loop(db)