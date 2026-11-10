from errors.journal_error import JournalError

class AIError(JournalError):
    def __init__(self, message, retry=False):
        JournalError.__init__(self, message)
        self._retry = retry

    @property
    def retry(self):
        return self._retry