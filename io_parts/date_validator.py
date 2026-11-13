from datetime import datetime
from io_parts.validator import Validator

class DateValidator(Validator):
    def __init__(self, allow_blank=False):
        Validator.__init__(self, "Enter a date like 2026-10-23, or press Enter.",
                           allow_blank)

    def is_valid(self, text):
        if len(text) != 10:
            return False
        try:
            datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            return False
        return True