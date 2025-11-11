import os
import logging
from getpass import getpass
import mmap
import secrets

from .SqliteDatabase import SqliteDatabase
from .EntryDto import EntryDto
from . import SqlStatements
from .utils import *

ENCRYPTED_DB_FILE = get_internal_file('db', 'safepass.db.enc')
SALT_FILE = get_internal_file('db', 'safepass.salt.bin')
BREACH_LIST_FILE = get_internal_file('res', '100k-most-used-passwords-NCSC.txt')

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format=f'(%(levelname)s) %(message)s',
    level=logging.INFO
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
    LOGGER.info('Encrypted database and salt file created. We recommend you to back them up.')
    main_loop(db)

def get_new_master_password() -> str:
    # https://pages.nist.gov/800-63-4/sp800-63b/passwords/
    # Can't apply rate limiting because its a binary
    
    while True:
        master_pwd = getpass('Please create a master password: ') # Getpass instead of input
        if len(master_pwd) < 15:
            LOGGER.warning('Entered password must be at least 15 characters long')
            continue
        with open(BREACH_LIST_FILE, 'rb') as file, \
            mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s: # Explain why mmap (https://stackoverflow.com/a/4944929)
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
        
def offer_new_database():
    if yes_no_question('Do you want to create an empty database? [Y/N] '):
        new_database()
        
def main_loop(db: SqliteDatabase):
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
            case '2' | 'N': insert_account(db)
            case '3' | 'R': remove_account(db)
            case '4' | 'D': dump_database(db)
            case '5' | 'C': change_master_password(db)
            case '6' | 'Q': exit(0)
            case _: welcome_msg()   
            
        input('Press any key to continue...\n')

def get_password(db: SqliteDatabase):
    service = input('Enter the name of the service or its domain: ')
    empty_results = True
    for row in db.execute(SqlStatements.SELECT_ENTRY, (service, service)):
        empty_results = False
        dto = EntryDto(row)
        print(f'{dto}\n')
    if empty_results:
        LOGGER.info('No entries were found for %s\n', service)

def insert_account(db: SqliteDatabase):
    entry = EntryDto()
    entry.service_name = input('Name of the service: ')
    res = db.execute(SqlStatements.CHECK_SERVICE_EXISTS, (entry.service_name,)).fetchone()
    service_exists = res is not None
    if not service_exists:
        entry.url = input('Domain of the service: ')
        entry.url = None if entry.url == '' else entry.url
        db.execute(SqlStatements.INSERT_SERVICE, (entry.service_name, entry.url))
    entry.username = input('Username: ')
    entry.password = getpass('Password (leave empty to generate one): ')
    remove_control_chars(entry.password) # Control chars cannot be used in passwords
    
    if entry.password == '' and yes_no_question('Generate password? [Y/N]'):
        entry.password = secrets.token_urlsafe(32) # Well beyond NIST recommendation. Intended to be copy-pasted, thus no need to be memorable.
        LOGGER.info('Generated password: %s', entry.password)
    
    db.execute(SqlStatements.INSERT_ACCOUNT, (entry.service_name, entry.username, entry.password))
    db.backup(ENCRYPTED_DB_FILE)
    LOGGER.info(f'New entry created for {entry.service_name} succesfully.')

def remove_account(db: SqliteDatabase):
    accounts = []
    service = input('Enter the name of the service or its domain: ')
    
    for row in db.execute(SqlStatements.SELECT_ENTRY, (service, service)):
        accounts.append(EntryDto(row))
        
    if len(accounts) == 0:
        LOGGER.info('No entries were found for %s.\n', service)
        return
    if len(accounts) == 1:
        db.execute(SqlStatements.DELETE_ACCOUNT, (accounts[0].account_id,))
        db.backup(ENCRYPTED_DB_FILE)
        LOGGER.info('Account in %s removed.\n', service)
        return
    
    for i, acc in enumerate(accounts, 1): # start=1 is more user friendly (?)
        print(f'[{i}] {acc.username}')
        
    while True:
        choice = input(f'Which account to delete? [1-{len(accounts)}] ')
        try:
            choice = int(choice)
            if 1 <= choice <= len(accounts):
                break
        except ValueError:
            continue
        
    choice_acc = accounts[choice - 1]
    db.execute(SqlStatements.DELETE_ACCOUNT, (choice_acc.account_id,))
    db.backup(ENCRYPTED_DB_FILE)
    LOGGER.info('Account in %s under "%s" deleted.\n', service, choice_acc.username)
    

def dump_database(db: SqliteDatabase):
    empty_results = True
    for row in db.execute(SqlStatements.SELECT_ALL):
        empty_results = False
        dto = EntryDto(row)
        print(f'{dto}\n')
    if empty_results:
        LOGGER.info('Database is empty\n')  

def change_master_password(db: SqliteDatabase):
    master_pwd = get_new_master_password()
    salt = db.change_master_pwd(ENCRYPTED_DB_FILE, master_pwd)
    write_binary(SALT_FILE, salt)
    LOGGER.info('Master password changed, new database and salt files created. We recommend you to back them up.')

def main():
    try:
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
            
            if db := SqliteDatabase.from_backup(ENCRYPTED_DB_FILE, SALT_FILE, master_pwd):
                break
            LOGGER.error('Wrong password, or the database has been tampered with. Restore a backup or create a new database.')
                
        main_loop(db)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()