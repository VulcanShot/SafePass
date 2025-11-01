from abc import ABC, abstractmethod

class EncryptedInMemDb(ABC):
    '''Interface for in-memory databases encrypted with Fernet'''
    @staticmethod
    @abstractmethod
    def from_script(script, crypto):
        pass
    
    @abstractmethod
    def execute(self, statement):
        pass
    
    @abstractmethod
    def execute_script(self, script):
        pass
    
    @abstractmethod
    def commit(self):
        pass
    
    @abstractmethod
    def rollback(self):
        pass
    
    @abstractmethod
    def backup(self, file, crypto):
        pass

    @abstractmethod
    def close(self):
        pass