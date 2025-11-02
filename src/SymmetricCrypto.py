from abc import ABC, abstractmethod

class SymmetricCrypto(ABC):
    '''Interface for a symmetric cryptography provider'''
    def __init__(self, key):
        self.key = key
        super().__init__()
        
    @staticmethod
    @abstractmethod
    def from_pwd(pwd, salt):
        pass
    
    @abstractmethod
    def encrypt(self, blob):
        pass
    
    @abstractmethod
    def decrypt_to_str(self, blob):
        pass