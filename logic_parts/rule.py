from abc import ABC, abstractmethod

class Rule(ABC):
    @abstractmethod
    def check(self, analysis, mood):
        pass

    def name(self):
        return self.__class__.__name__