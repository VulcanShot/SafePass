import os
import logging
from getpass import getpass
import mmap

from SqliteDatabase import SqliteDatabase
import SqlStatement

ENCRYPTED_DB_FILE = os.path.join('db', 'safepass.db.enc')
SALT_FILE = os.path.join('db', 'salt.bin')

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format=f'[{os.path.basename(__file__)}] (%(levelname)s) %(message)s',
    level=logging.DEBUG
)

def welcome():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Welcome to SafePass')

def change_working_dir():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
def new_database():
    master_pwd = get_new_master_password()
    (db, salt) = SqliteDatabase.from_script(SqlStatement.CREATE_TABLES, master_pwd)
    write_salt(salt)
    db.backup(ENCRYPTED_DB_FILE)
    welcome()
    print('Encrypted database and salt file created. We recommend you to back them up.')
    main_loop(db)

def get_new_master_password():
    #NOTE: https://pages.nist.gov/800-63-4/sp800-63b/passwords/
    # Can't apply rate limiting because its a binary (easily bypassable)
    
    while True:
        master_pwd = getpass('Please create a master password: ') # NOTE: Getpass instead of input
        if len(master_pwd) < 15:
            LOGGER.warning('Entered password must be at least 15 characters long')
            continue
        with open(os.path.join('res', '100k-most-used-passwords-NCSC.txt'), 'rb') as file, \
            mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s: # NOTE: Explain why mmap (https://stackoverflow.com/a/4944929)
            if s.find(master_pwd.encode()) != -1:
                LOGGER.warning('Entered password has been breached before')
                continue
        break

    while True:
        confirm_pwd = getpass('Confirm your master password: ')
        if confirm_pwd == master_pwd:
            break
        LOGGER.warning('Entered password does not match the master password.')
            
    return master_pwd
      
def write_salt(salt: bytes):
    with open(SALT_FILE, 'wb') as f:
        return f.write(salt)
        
def offer_new_database():
    yes = ['y', 'yes']
    choice = input('Do you want to create an empty database? [Y/N] ').lower()
    if choice in yes:
        new_database()
        
def main_loop(db):
    # TODO
    print('Please select the action you want to take:')
    print('[1] Get my password') # TODO: Show encrypted version too (as per Moodle)
    print('[2] Add new entry') # TODO: Password Generation
    print('[3] Remove entry')
    exit(0)

if __name__ == '__main__':
    try:
        change_working_dir()
        welcome()
        
        if not os.path.exists(ENCRYPTED_DB_FILE):
            # NOTE: If there is salt but no db, salt is ignored for security
            new_database()

        if not os.path.exists(SALT_FILE):
            LOGGER.error(f'The salt file ({SALT_FILE}) has not been found. Please restore it or create a new database.')
            offer_new_database()
            exit(2) # NOTE: Actual Windows exit code for file not found
            
        while True:
            master_pwd = getpass('Please enter your master password (leave empty to create new database): ')
            if len(master_pwd) == 0:
                offer_new_database()
                exit(1)
            db = SqliteDatabase.from_backup(ENCRYPTED_DB_FILE, master_pwd, SALT_FILE)
            if db:
                break
            LOGGER.error('Wrong password, or the database has been tampered with. Restore a backup or create a new database.')
                
        main_loop(db)
    except KeyboardInterrupt:
        pass