from settings import Settings
from io_parts.choice_validator import ChoiceValidator
from settings import Settings

class IOManager:
    WIDTH = 58
    MENU_CHOICES = ("1", "2", "3", "4", "q")
    
    def __init__(self, question_bank, settings=None, read=None, write=None):
        if settings is None:
            settings = Settings(env={})
        self._bank = question_bank
        self._settings = settings
        self._read = read if read is not None else input
        self._write = write if write is not None else print

    def ask(self, question, validator):
        while True:
            raw = self._read("  " + question + "  > ").strip()
            if raw == "" and validator.allow_blank:
                return raw
            if validator.is_valid(raw):
                return raw
            self._write("  -> " + validator.error_message)

    def ask_menu(self):
        self._write("  [1] Log a moment    [2] View entries    [3] Weekly review")
        self._write("  [4] Get support     [q] Quit")
        choice = self.ask("", ChoiceValidator(
            IOManager.MENU_CHOICES, "Pick 1, 2, 3, 4, or q."))
        return choice.lower()

    def ask_name(self):
        name = self._read("\n  Welcome to MIRA! What's your name?  > ").strip()
        return name

    def show(self, text):
        self._write(text)

    def show_notice(self, text):
        self._write("  (" + text + ")")

        