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

    @staticmethod
    def _to_int(value):
        if value is None or value == "":
            return 0
        try:
            return int(float(str(value)))
        except (ValueError, OverflowError):
            return 0

    @classmethod
    def from_row(cls, row):
        entry = JournalEntry(
            str(row.get("id", "")),
            str(row.get("timestamp", "")),
            str(row.get("profile", "")),
            str(row.get("note", "")),
            cls._to_int(row.get("mood", "")),
            str(row.get("trigger_choice", "")),
            str(row.get("trigger_prompt", "")),
            str(row.get("followup_text", "")),
            str(row.get("followup_prompt", "")),
            str(row.get("clarity_choice", "")),
            str(row.get("clarity_text", "")),
            str(row.get("clarity_prompt", "")),
            str(row.get("close_text", "")),
            str(row.get("close_prompt", "")),
            str(row.get("mode_choice", "")),
        )
        labels = {
            "mood_label": str(row.get("mood_label", "")),
            "trigger_label": str(row.get("trigger_label", "")),
            "clarity_label": str(row.get("clarity_label", "")),
            "mode_label": str(row.get("mode_label", "")),
        }
        return cls(entry, AIAnalysis.from_row(row),
                   str(row.get("outcome", "")),
                   cls._to_int(row.get("score", "")), labels)

    @property
    def entry(self):
        return self._entry

    @property
    def analysis(self):
        return self._analysis

    @property
    def outcome(self):
        return self._outcome

    @property
    def score(self):
        return self._score

    @property
    def id(self):
        return self._entry.id

    @property
    def timestamp(self):
        return self._entry.timestamp

    @property
    def date(self):
        return str(self._entry.timestamp)[:10]

    @property
    def mood(self):
        return self._entry.mood

    @property
    def trigger_label(self):
        return self._labels.get("trigger_label", "")

    @property
    def clarity_label(self):
        return self._labels.get("clarity_label", "")