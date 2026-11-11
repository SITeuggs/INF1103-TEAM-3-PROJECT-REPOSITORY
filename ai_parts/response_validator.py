import json
from errors.ai_error import AIError

class ResponseValidator:
    ENTRY_SENTIMENTS = ("positive", "neutral", "negative")
    ENTRY_CONGRUENCE = ("aligned", "diverged")
    ENTRY_OUTCOMES = ("accept", "flag", "check_in")
    ENTRY_TAGS = ("work", "sleep", "exercise", "social", "study", "rest")
    WEEKLY_KEYS = ("dominant_pattern", "best_mechanism", "friction_point",
                   "summary", "carry_forward")

    def __init__(self, required_keys=(), allowed=None, list_keys=(),
                 text_keys=(), cleaned=None):
        self._required_keys = tuple(required_keys)
        self._allowed = dict(allowed) if allowed is not None else {}
        self._list_keys = tuple(list_keys)
        self._text_keys = tuple(text_keys)
        self._cleaned = dict(cleaned) if cleaned is not None else {}

    @classmethod
    def for_entry(cls):
        return cls(
            allowed={
                "sentiment": cls.ENTRY_SENTIMENTS,
                "congruence": cls.ENTRY_CONGRUENCE,
                "recommended_outcome": cls.ENTRY_OUTCOMES,
            },
            list_keys=("emotions", "themes"),
            text_keys=("reflection",),
            cleaned={"tag_ai": (cls.ENTRY_TAGS, "rest")},
        )

    @classmethod
    def for_weekly(cls):
        return cls(required_keys=cls.WEEKLY_KEYS)

    def parse(self, text):
        if text is None:
            raise AIError("the AI sent an empty reply", retry=True)
        text = str(text).strip()
        if text[:3] == "```":
            parts = text.split("```")
            if len(parts) > 1:
                text = parts[1]
            if text[:4].lower() == "json":
                text = text[4:]
            text = text.strip()
        try:
            return json.loads(text)
        except ValueError:
            raise AIError("the AI reply was not valid JSON", retry=True)

    def validate(self, data):
        if not isinstance(data, dict):
            return False
        for key in self._required_keys:
            if key not in data.keys():
                return False
        for key in self._allowed.keys():
            if data.get(key, "") not in self._allowed[key]:
                return False
        for key in self._list_keys:
            if not isinstance(data.get(key, None), list):
                return False
        for key in self._text_keys:
            if not isinstance(data.get(key, None), str):
                return False
        for key in self._cleaned.keys():
            allowed_values = self._cleaned[key][0]
            default = self._cleaned[key][1]
            value = str(data.get(key, "")).lower().strip()
            if value not in allowed_values:
                value = default
            data[key] = value
        return True
