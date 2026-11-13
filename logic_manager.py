from logic_parts.history_analyser import HistoryAnalyser
from logic_parts.lowest_mood_rule import LowestMoodRule
from logic_parts.mismatch_rule import MismatchRule
from logic_parts.question_bank import QuestionBank
from logic_parts.stress_low_mood_rule import StressLowMoodRule
from logic_parts.support_policy import SupportPolicy
from models.entry_record import EntryRecord
from settings import Settings

class LogicManager:
    SEVERITY = {"accept": 0, "check_in": 1, "flag": 2}

    def __init__(self, settings=None, question_bank=None, rules=None):
        if settings is None:
            settings = Settings(env={})
        self._settings = settings
        self._bank = question_bank if question_bank is not None else QuestionBank()
        if rules is None:
            rules = [
                MismatchRule("negative", 4, True),
                MismatchRule("positive", 2, False),
                LowestMoodRule(),
                StressLowMoodRule(settings.STRESS_THEMES),
            ]
        self._rules = list(rules)
        self._support = SupportPolicy(settings)
        self._history = HistoryAnalyser(settings)

    @property
    def question_bank(self):
        return self._bank

    @property
    def minimum_for_review(self):
        return self._settings.MIN_ENTRIES_FOR_REVIEW