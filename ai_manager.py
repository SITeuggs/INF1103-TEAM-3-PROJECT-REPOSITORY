from ai_parts.prompt_builder import PromptBuilder
from ai_parts.response_validator import ResponseValidator
from errors.ai_error import AIError
from models.ai_analysis import AIAnalysis
from settings import Settings
import content

class AIManager:
    def __init__(self, client, question_bank, settings=None,
                 entry_validator=None, weekly_validator=None):
        if settings is None:
            settings = Settings(env={})
        self._client = client
        self._settings = settings
        self._builder = PromptBuilder(question_bank)
        self._entry_validator = entry_validator if entry_validator is not None else ResponseValidator.for_entry()
        self._weekly_validator = weekly_validator if weekly_validator is not None else ResponseValidator.for_weekly()
        self._warnings = []

    @property
    def warnings(self):
        return list(self._warnings)

    def enrich(self, entry):
        self._warnings = []
        payload = self._builder.entry_payload(entry)
        for attempt in range(1, self._settings.AI_MAX_ATTEMPTS + 1):
            try:
                raw = self._client.generate(content.SYSTEM_PROMPT, payload,
                                            self._settings.ENTRY_MAX_TOKENS)
            except Exception as error:
                self._warnings.append("AI error: " + str(error)
                                      + ", attempt " + str(attempt))
                break
            try:
                data = self._entry_validator.parse(raw)
            except AIError as error:
                self._warnings.append("AI response not valid JSON, attempt "
                                      + str(attempt))
                if error.retry:
                    continue
                break
            if self._entry_validator.validate(data):
                return AIAnalysis.from_dict(data)
            self._warnings.append("AI response invalid, attempt " + str(attempt))
        self._warnings.append("Using fallback, AI could not process this entry")
        return AIAnalysis.fallback()

    def weekly_synthesis(self, records, trajectory):
        self._warnings = []
        payload = self._builder.weekly_payload(records, trajectory)
        if not payload:
            return None
        try:
            raw = self._client.generate(content.WEEKLY_PROMPT, payload,
                                        self._settings.WEEKLY_MAX_TOKENS)
            data = self._weekly_validator.parse(raw)
        except Exception as error:
            self._warnings.append("Weekly synthesis error: " + str(error))
            return None
        if self._weekly_validator.validate(data):
            return data
        self._warnings.append("Weekly synthesis response missing fields")
        return None
