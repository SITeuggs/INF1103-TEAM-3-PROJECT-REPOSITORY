from abc import ABC, abstractmethod

class RecordStorage(ABC):
    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def load_all(self):
        pass

    @abstractmethod
    def save(self, row):
        pass

    @abstractmethod
    def update(self, entry_id, fields):
        pass

    @abstractmethod
    def delete(self, entry_id):
        pass
