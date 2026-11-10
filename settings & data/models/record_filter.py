class RecordFilter:
    def __init__(self, outcome=None, min_mood=None, max_mood=None,
                 since=None, until=None, keyword=None):
        self._outcome = outcome
        self._min_mood = min_mood
        self._max_mood = max_mood
        self._since = since
        self._until = until
        self._keyword = keyword

    def is_empty(self):
        return (self._outcome is None and self._min_mood is None
                and self._max_mood is None and self._since is None
                and self._until is None and self._keyword is None)

    def _mentions(self, record, word):
        word = word.lower()
        if word in record.entry.note.lower():
            return True
        for theme in record.analysis.lowered_themes():
            if word in theme:
                return True
        return False

    def matches(self, record):
        if self._outcome is not None and record.outcome != self._outcome:
            return False
        if self._min_mood is not None and record.mood < self._min_mood:
            return False
        if self._max_mood is not None:
            if record.mood == 0 or record.mood > self._max_mood:
                return False
        if self._since is not None and record.date < self._since:
            return False
        if self._until is not None and record.date > self._until:
            return False
        if self._keyword is not None and not self._mentions(record, self._keyword):
            return False
        return True
