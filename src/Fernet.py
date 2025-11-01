from SymmetricCrypto import SymmetricCrypto
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class FernetCrypto(SymmetricCrypto):
    '''Fernet cryptography'''
    @staticmethod
    def from_pwd(pwd, salt):
        #NOTE: Explain why key derivation
        # Reference: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_200_000, #NOTE: Django recommendation
        )
        
        key = kdf.derive(bytes(pwd, 'utf-8'))
        encoded_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(encoded_key)
        return (FernetCrypto(fernet), salt)
    
    def encrypt(self, blob):
        self.key.encrypt(blob)
    
    def decrypt(self, blob):
        self.key.decrypt(blob)