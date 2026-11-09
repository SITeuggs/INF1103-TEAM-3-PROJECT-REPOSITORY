class AIAnalysis:
    def __init__(self, sentiment="neutral", emotions=None, themes=None,
                 congruence="aligned", congruence_note="", tag_ai="rest",
                 recommended_outcome="accept", reasoning="",
                 reflection="", reframe=""):
        self._sentiment = sentiment
        self._emotions = []
        if emotions is not None:
            for e in emotions:
                self._emotions.append(str(e))
        self._themes = []
        if themes is not None:
            for t in themes:
                self._themes.append(str(t))
        self._congruence = congruence
        self._congruence_note = congruence_note
        self._tag_ai = tag_ai
        self._recommended_outcome = recommended_outcome
        self._reasoning = reasoning
        self._reflection = reflection
        self._reframe = reframe

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("sentiment", "neutral"),
            data.get("emotions", []),
            data.get("themes", []),
            data.get("congruence", "aligned"),
            data.get("congruence_note", ""),
            data.get("tag_ai", "rest"),
            data.get("recommended_outcome", "accept"),
            data.get("reasoning", ""),
            data.get("reflection", ""),
            data.get("reframe", ""),
        )

    @classmethod
    def from_row(cls, row):
        emotions = []
        if row.get("emotions", ""):
            emotions = str(row["emotions"]).split("|")
        themes = []
        if row.get("themes", ""):
            themes = str(row["themes"]).split("|")
        return cls(
            row.get("sentiment", ""),
            emotions,
            themes,
            row.get("congruence", ""),
            row.get("congruence_note", ""),
            row.get("tag_ai", ""),
            row.get("recommended_outcome", ""),
            row.get("reasoning", ""),
            row.get("reflection", ""),
            row.get("reframe", ""),
        )

    @classmethod
    def fallback(cls):
        return cls(reasoning="AI fallback — could not process")


    @property
    def sentiment(self):
        return self._sentiment

    @property
    def emotions(self):
        return list(self._emotions)

    @property
    def themes(self):
        return list(self._themes)

    @property
    def congruence(self):
        return self._congruence

    @property
    def congruence_note(self):
        return self._congruence_note

    @property
    def tag_ai(self):
        return self._tag_ai

    @property
    def recommended_outcome(self):
        return self._recommended_outcome

    @property
    def reasoning(self):
        return self._reasoning

    @property
    def reflection(self):
        return self._reflection

    @property
    def reframe(self):
        return self._reframe

    def to_fields(self):
        return {
            "sentiment": self._sentiment,
            "emotions": "|".join(self._emotions),
            "themes": "|".join(self._themes),
            "congruence": self._congruence,
            "congruence_note": self._congruence_note,
            "tag_ai": self._tag_ai,
            "recommended_outcome": self._recommended_outcome,
            "reasoning": self._reasoning,
            "reflection": self._reflection,
            "reframe": self._reframe,
        }