from io_parts.validator import Validator

class NonEmptyValidator(Validator):
    def __init__(self, error_message="Write at least a few words.",
                 allow_blank=False):
        Validator.__init__(self, error_message, allow_blank)

    def is_valid(self, text):
        return len(text) > 0