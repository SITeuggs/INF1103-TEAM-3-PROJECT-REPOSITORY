from models.ai_analysis import AIAnalysis
from models.journal_entry import JournalEntry

class EntryRecord:
    FIELDNAMES = [
        "id", "timestamp", "profile",
        "note",
        "mood", "mood_label",
        "trigger_prompt", "trigger_choice", "trigger_label",
        "followup_prompt", "followup_text",
        "clarity_choice", "clarity_label",
        "clarity_prompt", "clarity_text",
        "close_prompt", "close_text",
        "mode_choice", "mode_label",
        "sentiment", "emotions", "themes",
        "congruence", "congruence_note",
        "tag_ai", "recommended_outcome", "reasoning",
        "reflection", "reframe",
        "outcome", "score",
    ]

    def __init__(self, entry, analysis, outcome, score, labels):
        self._entry = entry
        self._analysis = analysis
        self._outcome = outcome
        self._score = score
        self._labels = dict(labels)