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

    def test_row_round_trip(self):
        record = self.make_record(
            4,
            "2026-10-22T08:30:00",
            "check_in",
            3,
            "negative",
            "A reading.",
            ["work", "stress"],
        )
        rebuilt = EntryRecord.from_row(record.to_row())
        self.assertEqual(rebuilt.id, record.id)
        self.assertEqual(rebuilt.mood, 4)
        self.assertEqual(rebuilt.score, 3)
        self.assertEqual(rebuilt.outcome, "check_in")
        self.assertEqual(rebuilt.analysis.themes, ["work", "stress"])
        self.assertEqual(rebuilt.analysis.reflection, "A reading.")
        self.assertEqual(rebuilt.trigger_label, record.trigger_label)
        self.assertEqual(rebuilt.to_row(), record.to_row())

    def test_recent_analysed_takes_the_latest(self):
        journal = Journal(
            [
                self.make_record(1, "2026-10-01T10:00:00"),
                self.make_record(2, "2026-10-02T10:00:00"),
                self.make_record(3, "2026-10-03T10:00:00"),
            ]
        )
        recent = journal.recent_analysed(2)
        self.assertEqual([recent[0].mood, recent[1].mood], [2, 3])
        self.assertEqual(journal.recent_analysed(0), [])

    def test_keyword_finds_an_ai_theme(self):
        journal = Journal(
            [
                self.make_record(2, "2026-10-18T10:00:00", themes=["exams", "stress"]),
                self.make_record(3, "2026-10-19T10:00:00", themes=["friends"]),
                self.make_record(4, "2026-10-20T10:00:00", themes=[]),
            ]
        )
        found = []
        for record in journal.filter(RecordFilter(keyword="exams")):
            found.append(record.mood)
        self.assertEqual(found, [2])

    def test_corrupt_file_gives_empty_settings(self):
        with open(self.config_path, "w") as f:
            f.write("{this is not json")
        self.assertEqual(ConfigStore(self.config_path).load(), {})

    def test_create_and_read(self):
        storage = self.memory_storage()
        row = self.make_record(4, "2026-10-22T08:00:00").to_row()
        storage.save(row)
        rows = storage.load_all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], row["id"])
        self.assertEqual(rows[0]["mood"], "4")

    def test_update(self):
        storage = self.memory_storage()
        row = self.make_record(3).to_row()
        storage.save(row)
        self.assertTrue(storage.update(row["id"], {"outcome": "flag", "score": 1}))
        changed = storage.load_all()[0]
        self.assertEqual((changed["outcome"], changed["score"]), ("flag", "1"))

    def test_delete(self):
        storage = self.memory_storage()
        row = self.make_record(3).to_row()
        storage.save(row)
        self.assertTrue(storage.delete(row["id"]))
        self.assertEqual(storage.load_all(), [])
        self.assertFalse(storage.delete(row["id"]))

    def test_a_corrupt_file_raises_instead_of_crashing(self):
        path = os.path.join(self.folder, "journal.db")
        with open(path, "wb") as f:
            f.write(b"this is definitely not a sqlite database file" * 20)
        storage = SQLiteStorage(path)
        self.addCleanup(storage.close)
        with self.assertRaises(StorageError):
            storage.load_all()

    def test_a_failed_save_keeps_the_record_for_the_session(self):
        blocker = os.path.join(self.folder, "blocker")
        with open(blocker, "w") as f:
            f.write("a file, not a folder")
        storage = SQLiteStorage(os.path.join(blocker, "journal.db"))
        data = DataManager(storage, ConfigStore(self.config_path))
        self.assertFalse(data.add_record(self.make_record(3)))
        self.assertEqual(data.journal.count(), 1)
        self.assertIn("Could not open the database", data.last_error)

    def test_it_holds_fifteen_entries(self):
        storage = self.memory_storage()
        data = DataManager(storage, ConfigStore(self.config_path))
        data.load_samples(self.SAMPLE_FILE, date(2026, 11, 6))
        self.assertEqual(data.journal.count(), 15)
        self.assertEqual(len(storage.load_all()), 15)

    def test_liskov_any_storage_can_stand_in_for_another(self):
        file_storage = SQLiteStorage(os.path.join(self.folder, "journal.db"))
        self.addCleanup(file_storage.close)
        for storage in (self.memory_storage(), file_storage):
            with self.subTest(storage.describe()):
                self.assertIsInstance(storage, RecordStorage)
                storage.save(self.make_record(3).to_row())
                self.assertEqual(len(storage.load_all()), 1)

if __name__ == "__main__":
    unittest.main()
