from SymmetricCrypto import SymmetricCrypto
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class FernetCrypto(SymmetricCrypto):
    '''Fernet cryptography'''
    @staticmethod
    def from_pwd(pwd, salt = None):
        #NOTE: Explain why key derivation
        # Reference: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        
        if salt is None:
            salt = os.urandom(16)
            is_salt_new = True
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_200_000, #NOTE: Django recommendation
        )
        
        key = kdf.derive(bytes(pwd, 'utf-8'))
        encoded_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(encoded_key)
        return FernetCrypto(fernet) if not is_salt_new else (FernetCrypto(fernet), salt)
    
    def encrypt(self, blob):
        return self.key.encrypt(blob)
    
    def decrypt(self, token):
        '''
        Returns the decrypted plaintext, or None if there was an problem with the token.
        '''
        try:
            return self.key.decrypt(token)
        except InvalidToken:
            return None