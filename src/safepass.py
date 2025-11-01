import os
from SqliteDatabase import SqliteDatabase
from Fernet import FernetCrypto
import logging

'''
-- Account
AccountID : PK
ServiceID : FK
Username : STR
Password : STR

-- Service
ServiceID : PK
Name : STR UNIQUE
Domain : STR
'''

# Include that I considered using command-line arguments to add entries, but that would be insecure becase of `history`. Doing it only for retreival would be inconsistent.
# Retrieve db to memory, decrypt it and work in memory. When quitting, simple encrypt it and write it down again.

ENCRYPTED_DB_FILE = os.path.join('db', 'safepass.db.enc')
SALT_FILE = os.path.join('db', 'salt.bin')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format=f'[{os.path.basename(__file__)}] (%(levelname)s) %(message)s',
    level=logging.DEBUG
)
        
def write_salt(salt: bytes):
    with open(SALT_FILE, 'wb') as f:
        return f.write(salt)

def get_salt():
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    return None
        
def load_database(crypto: FernetCrypto):
    db = SqliteDatabase.open()
    if os.path.exists(ENCRYPTED_DB_FILE):
        try:
            with open(ENCRYPTED_DB_FILE, 'rb') as f:
                blob = f.read()
                crypto.decrypt(blob)
            db.from_dump()
        except InvalidToken:
            LOGGER.warning('Fernet token is malformed, or it does not have a valid signature.')
    LOGGER.info('Database not found, creating a new one')
    return db

print('Please select the action you want to take:')
print('[1] Add new password entry')
print('[2] Get my password')

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Welcome to SafePass')
    master_pwd = input('Please enter your master password: ')
    salt_from_file = get_salt()
    (crypto, salt) = FernetCrypto.from_pwd(master_pwd, salt_from_file)
    if not salt_from_file:
        write_salt(salt)
    db = load_database(crypto)