from logic_parts.rule import Rule

class StressLowMoodRule(Rule):
    def __init__(self, stress_words):
        self._stress_words = stress_words

    def check(self, analysis, mood):
        if mood > 2:
            return None
        for theme in analysis.lowered_themes():
            for word in self._stress_words:
                if word in theme:
                    return "flag"
        return None
