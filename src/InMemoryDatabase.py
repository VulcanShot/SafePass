from abc import ABC, abstractmethod

class InMemoryDatabase(ABC):
    '''Interface for in-memory databases'''
    @staticmethod
    @abstractmethod
    def open():
        pass
    
    @abstractmethod
    def load_dump(self, dump):
        pass
    
    @abstractmethod
    def execute(self, statement):
        pass
    
    @abstractmethod
    def commit(self):
        pass
    
    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def close(self):
        pass