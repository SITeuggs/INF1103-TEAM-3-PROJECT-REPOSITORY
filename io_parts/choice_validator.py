from io_parts.validator import Validator

class ChoiceValidator(Validator):
    def __init__(self, choices, error_message, allow_blank=False):
        Validator.__init__(self, error_message, allow_blank)
        self._choices = []
        for choice in choices:
            self._choices.append(str(choice).upper())

    def is_valid(self, text):
        return text.upper() in self._choices
