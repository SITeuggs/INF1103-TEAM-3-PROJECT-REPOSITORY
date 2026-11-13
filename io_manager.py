from settings import Settings

class IOManager:
    WIDTH = 58

    def __init__(self, question_bank, settings=None, read=None, write=None):
        if settings is None:
            settings = Settings(env={})
        self._bank = question_bank
        self._settings = settings
        self._read = read if read is not None else input
        self._write = write if write is not None else print

    def show(self, text):
        self._write(text)

    def show_notice(self, text):
        self._write("  (" + text + ")")