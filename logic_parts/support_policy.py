class SupportPolicy:
    def __init__(self, settings):
        self._streak_length = settings.STREAK_LENGTH

    def has_low_mood_streak(self, records):
        last = records[-self._streak_length:]
        if len(last) < self._streak_length:
            return False
        for r in last:
            past_mood = r.mood
            if not past_mood:
                past_mood = 3
            if past_mood > 2:
                return False
        return True

    def needs_support(self, record, previous_records):
        if record.mood == 1:
            return True
        if record.score <= 2:
            return True
        if record.outcome == "flag":
            return True
        if self.has_low_mood_streak(previous_records):
            return True
        return False
