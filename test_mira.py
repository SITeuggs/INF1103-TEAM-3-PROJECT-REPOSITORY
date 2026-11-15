import ast
import json
import os
import shutil
import tempfile
import unittest
from ai_manager import AIManager
from ai_parts.ai_client import AIClient
from ai_parts.fake_ai_client import FakeAIClient
from ai_parts.gemini_client import GeminiClient
from ai_parts.response_validator import ResponseValidator
from data_manager import DataManager
from data_parts.config_store import ConfigStore
from data_parts.record_storage import RecordStorage
from data_parts.sqlite_storage import SQLiteStorage
from datetime import date
from datetime import datetime
from errors.ai_error import AIError
from errors.storage_error import StorageError
from io_manager import IOManager
from io_parts.choice_validator import ChoiceValidator
from io_parts.date_validator import DateValidator
from logic_manager import LogicManager
from logic_parts.history_analyser import HistoryAnalyser
from logic_parts.question_bank import QuestionBank
from logic_parts.support_policy import SupportPolicy
from main import JournalApp
from models.ai_analysis import AIAnalysis
from models.entry_record import EntryRecord
from models.journal import Journal
from models.journal_entry import JournalEntry
from models.record_filter import RecordFilter
from settings import Settings


class MiraTests(unittest.TestCase):
    NOW = datetime(2026, 10, 23, 9, 0, 0)
    PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_FILE = os.path.join(PROJECT_FOLDER, "sample_entries.json")

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder)
        self.config_path = os.path.join(self.folder, "config.json")
        self.answers = []
        self.prompts = []
        self.lines = []
        self.made = 0

    def read(self, prompt=""):
        self.prompts.append(prompt)
        if not self.answers:
            raise EOFError("no more scripted answers")
        answer = self.answers[0]
        del self.answers[0]
        if isinstance(answer, BaseException):
            raise answer
        return answer

    def write(self, text=""):
        self.lines.append(str(text))

    def clock(self):
        return self.NOW

    def output(self):
        return "\n".join(self.lines)

    def memory_storage(self):
        storage = SQLiteStorage(":memory:")
        self.addCleanup(storage.close)
        return storage

    def good_reply(self, sentiment="neutral", outcome="accept", themes=None):
        if themes is None:
            themes = ["work"]
        return json.dumps(
            {
                "sentiment": sentiment,
                "emotions": ["tired"],
                "themes": themes,
                "congruence": "aligned",
                "congruence_note": "",
                "tag_ai": "work",
                "recommended_outcome": outcome,
                "reasoning": "sample",
                "reflection": "A grounded reading.",
                "reframe": "A sample reframe.",
            }
        )

    def weekly_reply(self):
        return json.dumps(
            {
                "dominant_pattern": "Work kept showing up.",
                "best_mechanism": "Writing it down helped.",
                "friction_point": "Late nights.",
                "summary": "A small sample of entries.",
                "carry_forward": "Evenings were calmer.",
            }
        )

    def make_record(
        self,
        mood=3,
        timestamp="2026-10-21T10:00:00",
        outcome="accept",
        score=None,
        sentiment="neutral",
        reflection="sample reflection",
        themes=None,
    ):
        self.made = self.made + 1
        if score is None:
            score = mood
        entry = JournalEntry(
            "t" + str(self.made).zfill(7),
            timestamp,
            "Test",
            "a note",
            mood,
            "A",
            "What pulled things down?",
            "",
            "",
            "A",
            "some words",
            "A question?",
            "a plan",
            "Another question?",
            "A",
        )
        analysis = AIAnalysis(
            sentiment,
            ["tired"],
            themes,
            "aligned",
            "",
            "work",
            "accept",
            "sample",
            reflection,
            "",
        )
        labels = {
            "mood_label": "a mood",
            "trigger_label": "An internal thought or worry",
            "clarity_label": "Yes — I can put it into words",
            "mode_label": "A straight, honest read",
        }
        return EntryRecord(entry, analysis, outcome, score, labels)

    def make_analysis(self, sentiment, themes=None, outcome="accept"):
        return AIAnalysis(
            sentiment,
            ["tired"],
            themes,
            "aligned",
            "",
            "work",
            outcome,
            "sample",
            "sample reflection",
            "sample reframe",
        )

    def make_entry(self, mood=4):
        return JournalEntry(
            "e1",
            "2026-10-23T09:00:00",
            "Test",
            "A long day.",
            mood,
            "A",
            "What clicked?",
            "",
            "What clicked?",
            "B",
            "maybe stress",
            "What would you call it?",
            "sleep more",
            "What do you want to carry?",
            "A",
        )

    def entry_answers(self, mood, trigger="A", followup=""):
        typed = ["A day.", "done", str(mood), trigger]
        if not (mood >= 4 and trigger == "D"):
            typed.append(followup)
        return typed + ["A", "some words", "a plan", "A"]

    def save_profile(self):
        ConfigStore(self.config_path).save({"profile": "Tester"})

    def build(self, typed, replies=None, storage=None, auto_samples=False):
        settings = Settings(env={})
        bank = QuestionBank()
        self.answers = list(typed)
        self.client = FakeAIClient(replies or [self.good_reply()])
        self.storage = storage if storage is not None else self.memory_storage()
        self.data = DataManager(self.storage, ConfigStore(self.config_path))
        io = IOManager(bank, settings, self.read, self.write)
        ai = AIManager(self.client, bank, settings)
        logic = LogicManager(settings, bank)
        return JournalApp(
            io, ai, logic, self.data, self.clock, self.SAMPLE_FILE, auto_samples
        )

    def stored(self, moods_and_days):
        storage = self.memory_storage()
        for item in moods_and_days:
            storage.save(self.make_record(item[0], item[1]).to_row())
        return storage

    def check_validator(self, validator, good, bad):
        for text in good:
            with self.subTest("good " + repr(text)):
                self.assertTrue(validator.is_valid(text))
        for text in bad:
            with self.subTest("bad " + repr(text)):
                self.assertFalse(validator.is_valid(text))

    def dated(self, count):
        records = []
        for number in range(count):
            records.append(
                self.make_record(3, "2026-10-" + str(number + 1).zfill(2) + "T10:00:00")
            )
        return Journal(records)


if __name__ == "__main__":
    unittest.main()
