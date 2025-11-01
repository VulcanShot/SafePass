from abc import ABC, abstractmethod

class InMemoryDatabase(ABC):
    '''Interface for in-memory databases'''
    @staticmethod
    @abstractmethod
    def open(script):
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
    def backup(self, file):
        pass

    @abstractmethod
    def close(self):
        pass