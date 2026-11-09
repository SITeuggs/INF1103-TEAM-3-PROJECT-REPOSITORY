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