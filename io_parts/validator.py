from abc import ABC, abstractmethod

class Validator(ABC):
    def __init__(self, error_message, allow_blank=False):
        self._error_message = error_message
        self._allow_blank = allow_blank

    @property
    def error_message(self):
        return self._error_message

    @property
    def allow_blank(self):
        return self._allow_blank

    @abstractmethod
    def is_valid(self, text):
        pass