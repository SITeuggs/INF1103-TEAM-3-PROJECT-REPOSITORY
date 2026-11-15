from logic_parts.rule import Rule

class MismatchRule(Rule):
    def __init__(self, sentiment, threshold, mood_is_high):
        self._sentiment = sentiment
        self._threshold = threshold
        self._mood_is_high = mood_is_high

    def check(self, analysis, mood):
        if analysis.sentiment != self._sentiment:
            return None
        if self._mood_is_high and mood >= self._threshold:
            return "check_in"
        if not self._mood_is_high and mood <= self._threshold:
            return "check_in"
        return None
