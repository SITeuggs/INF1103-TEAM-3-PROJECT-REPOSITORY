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

    def rules_outcome(self, analysis, mood):
        for rule in self._rules:
            result = rule.check(analysis, mood)
            if result is not None:
                return result
        return "accept"

    def adjust_score(self, mood, sentiment):
        score = mood
        if sentiment == "negative" and mood >= 3:
            score = score - 1
            if score < 1:
                score = 1
        elif sentiment == "positive" and mood <= 3:
            score = score + 1
            if score > 5:
                score = 5
        return score

    def severity(self, outcome):
        if outcome in LogicManager.SEVERITY.keys():
            return LogicManager.SEVERITY[outcome]
        return 0

    def more_serious(self, ai_outcome, rules_outcome):
        if self.severity(ai_outcome) > self.severity(rules_outcome):
            return ai_outcome
        return rules_outcome

    def evaluate(self, entry, analysis, journal):
        mood = entry.mood
        rules_outcome = self.rules_outcome(analysis, mood)
        ai_outcome = analysis.recommended_outcome
        outcome = self.more_serious(ai_outcome, rules_outcome)
        score = self.adjust_score(mood, analysis.sentiment)
        if self._support.has_low_mood_streak(journal.records) and outcome == "accept":
            outcome = "check_in"
        if score <= 2 and outcome == "accept":
            outcome = "check_in"
        return outcome, score

    def build_record(self, entry, analysis, outcome, score):
        return EntryRecord(entry, analysis, outcome, score,
                           self._bank.labels_for(entry))

    def needs_support(self, record, journal):
        return self._support.needs_support(record, journal.records)

    def plan_weekly(self, journal):
        return journal.recent_analysed(self._settings.WEEKLY_LIMIT)

    def trajectory(self, records):
        return self._history.trajectory(records)

    def mood_range(self, records):
        return self._history.mood_range(records)

    def average_mood(self, records):
        return self._history.average(records)

    def compare_weeks(self, journal, today):
        return self._history.compare_weeks(journal, today)

    def summarise_records(self, records):
        return self._history.summarise(records)
