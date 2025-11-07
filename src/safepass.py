import os
import logging
from getpass import getpass
import mmap
import secrets

from SqliteDatabase import SqliteDatabase
from EntryDto import EntryDto
import SqlStatements
from utils import *

# TODO LIST
# - key cycling (https://cryptography.io/en/latest/fernet/#cryptography.fernet.MultiFernet.rotate)
# - pedir feedback para reporte

ENCRYPTED_DB_FILE = os.path.join('db', 'safepass.db.enc')
SALT_FILE = os.path.join('db', 'salt.bin')

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format=f'[{os.path.basename(__file__)}] (%(levelname)s) %(message)s',
    level=logging.DEBUG
)

def welcome_msg():
    clear_screen()
    print('Welcome to SafePass')
    
def new_database():
    master_pwd = get_new_master_password()
    (db, salt) = SqliteDatabase.from_script(SqlStatements.CREATE_TABLES, master_pwd)
    write_binary(SALT_FILE, salt)
    db.backup(ENCRYPTED_DB_FILE)
    welcome_msg()
    print('Encrypted database and salt file created. We recommend you to back them up.')
    main_loop(db)

def get_new_master_password() -> str:
    # https://pages.nist.gov/800-63-4/sp800-63b/passwords/
    # Can't apply rate limiting because its a binary (easily bypassable)
    
    while True:
        master_pwd = getpass('Please create a master password: ') # Getpass instead of input
        # TODO: Remove this in prod
        # if len(master_pwd) < 15:
        #     LOGGER.warning('Entered password must be at least 15 characters long')
        #     continue
        # with open(os.path.join('res', '100k-most-used-passwords-NCSC.txt'), 'rb') as file, \
        #     mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s: # Explain why mmap (https://stackoverflow.com/a/4944929)
        #     if s.find(master_pwd.encode()) != -1:
        #         LOGGER.warning('Entered password has been breached before')
        #         continue
        break

    while True:
        confirm_pwd = getpass('Confirm your master password: ')
        if confirm_pwd == master_pwd:
            break
        LOGGER.warning('Entered password does not match the master password.')
            
    return master_pwd
        
def offer_new_database():
    if yes_no_question('Do you want to create an empty database? [Y/N] '):
        new_database()
        
def main_loop(db: SqliteDatabase):
    # TODO
    # db.execute("INSERT INTO Service (Name, url) VALUES ('Netflix', 'netflix.com')")
    # db.execute("INSERT INTO Account (ServiceId, Username, Password) VALUES (1, 'xXPipidinoXx', 'asdAsdASD')")
    
    while True:
        print('Please select the action you want to take:')
        print('[1] ' + underline_text('G') + 'et password')
        print('[2] ' + underline_text('N') + 'ew entry')
        print('[3] ' + underline_text('R') + 'emove entry')
        print('[4] ' + underline_text('D') + 'ump all passwords')
        print('[5] ' + underline_text('C') + 'hange master password')
        print('[6] ' + underline_text('Q') + 'uit')
        opt = input(':').upper() # NOTE: LESS-style, felt that it gives some ui feedback
        
        match opt:
            case '1' | 'G': get_password(db)
            case '2' | 'N': insert_entry(db)
            case '3' | 'R':
                service = input('Enter the name of the service or its domain: ')
                for row in db.execute(SqlStatements.DELETE_ENTRY, (service, service)):
                    print(row)
            case '4' | 'D':
                pass
            case '5' | 'C':
                pass
            case '6' | 'Q':
                exit(0)
            case _:
                welcome_msg()
                continue               

def get_password(db: SqliteDatabase):
    service = input('Enter the name of the service or its domain: ')
    for row in db.execute(SqlStatements.SELECT_ENTRY, (service, service)):
        dto = EntryDto(row)
        print(dto.service_name, end='')
        if dto.url != '' and dto.url != None :
            print(f' ({dto.url})')
        else: print()
        print('Username: ' + dto.username) # Did not print encrypted version too because I am encrypting whole db
        print('Password: ' + dto.password)
        print()
        # TODO: If no account exist, output something

def insert_entry(db: SqliteDatabase):
    entry = EntryDto()
    entry.service_name = input('Name of the service: ')
    service_exists = False
    for _ in db.execute(SqlStatements.SELECT_SERVICE, (entry.service_name,)):
        service_exists = True
    if not service_exists:
        entry.url = input('Domain of the service: ')
        db.execute(SqlStatements.INSERT_SERVICE, (entry.service_name, entry.url))
    entry.username = input('Username: ')
    entry.password = getpass('Password (leave empty to generate one): ')
    remove_control_chars(entry.password) # Control chars cannot be used in passwords
    
    if entry.password == '' and yes_no_question('Generate password? [Y/N]'):
        entry.password = secrets.token_urlsafe(32) # Well beyond NIST recommendation. Intended to be copy-pasted, thus no need to be memorable.
        LOGGER.info('Generated password: %s', entry.password)
    
    db.execute(SqlStatements.INSERT_ENTRY, (entry.service_name, entry.username, entry.password))
    db.backup(ENCRYPTED_DB_FILE)
    LOGGER.info(f'New entry created for {entry.service_name} succesfully.')

def main():
    try:
        change_working_dir()
        welcome_msg()
        
        if not os.path.exists(ENCRYPTED_DB_FILE):
            # If there is salt but no db, salt is ignored for security
            new_database()

        if not os.path.exists(SALT_FILE):
            LOGGER.error(f'The salt file ({SALT_FILE}) has not been found. Please restore it or create a new database.')
            offer_new_database()
            exit(2) # Actual Windows exit code for file not found
            
        while True:
            master_pwd = getpass('Please enter your master password (leave empty to create new database): ')
            if len(master_pwd) == 0:
                offer_new_database()
                exit(1)
            db = SqliteDatabase.from_backup(ENCRYPTED_DB_FILE, SALT_FILE, master_pwd)
            if db:
                break
            LOGGER.error('Wrong password, or the database has been tampered with. Restore a backup or create a new database.')
                
        main_loop(db)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()