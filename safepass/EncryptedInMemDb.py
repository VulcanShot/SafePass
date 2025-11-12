from abc import ABC, abstractmethod

class EncryptedInMemDb(ABC):
    '''Interface for in-memory databases encrypted with Fernet'''
    @staticmethod
    @abstractmethod
    def from_script(script: str, master_pwd: str):
        pass
    
    @staticmethod
    @abstractmethod
    def from_backup(backup_file: str, salt_file: str, master_pwd: str):
        pass
    
    @abstractmethod
    def change_master_pwd(self, backup_file: str, salt_file: str, master_pwd: str) -> bytes:
        pass
    
    @abstractmethod
    def execute(self, statement: str, params: dict = ()):
        pass
    
    @abstractmethod
    def execute_script(self, script: str):
        pass
    
    @abstractmethod
    def backup(self, filename: str) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass