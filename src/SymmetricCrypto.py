from abc import ABC, abstractmethod

class SymmetricCrypto(ABC):
    '''Interface for symmetric cryptography providers'''
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
    def decrypt(self, blob):
        pass