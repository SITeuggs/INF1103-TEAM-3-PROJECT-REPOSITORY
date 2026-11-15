from logic_parts.rule import Rule

class LowestMoodRule(Rule):
    def check(self, analysis, mood):
        if mood == 1:
            return "check_in"
        return None
