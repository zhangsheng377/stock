from abc import abstractmethod


class DataBase:
    @abstractmethod
    def __init__(self, database_name, sheet_name):
        pass

    @abstractmethod
    def insert(self, document):
        pass

    @abstractmethod
    def find(self, filter=None, sort=None):
        pass

    @abstractmethod
    def find_one(self, filter=None, sort=None):
        pass

    @abstractmethod
    def update_one(self, filter, update):
        pass

    @abstractmethod
    def delete(self, filter):
        pass
