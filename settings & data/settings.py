import os
from dotenv import load_dotenv

class Settings:
    WEEKLY_LIMIT = 7
    MIN_ENTRIES_FOR_REVIEW = 3
    COMPARE_DAYS = 7
    STREAK_LENGTH = 3
    STRESS_THEMES = ("stress", "pressure", "overwhelm")
    VOLATILE_SWING = 1.5
    TREND_CHANGE = 0.5
    MODEL = "gemini-3.5-flash-lite"
    AI_TIMEOUT_SECONDS = 30
    AI_MAX_ATTEMPTS = 2
    ENTRY_MAX_TOKENS = 800
    WEEKLY_MAX_TOKENS = 600
    HISTORY_LIMIT = 20

    def __init__(self, env=None):
        if env is None:
            load_dotenv()
            env = os.environ
        self._gemini_key = env.get("GEMINI_KEY")
        self._config_file = env.get("CONFIG_FILE", "config.json")
        self._database_file = env.get("DATABASE_FILE", "journal.db")
        self._sample_file = env.get("SAMPLE_FILE", "sample_entries.json")

    @property
    def gemini_key(self):
        return self._gemini_key

    @property
    def config_file(self):
        return self._config_file

    @property
    def database_file(self):
        return self._database_file

    @property
    def sample_file(self):
        return self._sample_file