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

    def test_outcome_rules(self):
        cases = [
            ("negative", 4, [], "check_in"),
            ("positive", 2, [], "check_in"),
            ("neutral", 1, [], "check_in"),
            ("negative", 2, ["stress"], "flag"),
            ("neutral", 2, ["work stress"], "flag"),
            ("negative", 2, ["overwhelmed"], "flag"),
            ("negative", 3, ["stress"], "accept"),
            ("positive", 5, [], "accept"),
            ("negative", 2, [], "accept"),
        ]
        logic = LogicManager(Settings(env={}))
        for case in cases:
            with self.subTest(case[0] + ", mood " + str(case[1]) + ", " + str(case[2])):
                analysis = self.make_analysis(case[0], case[2])
                self.assertEqual(logic.rules_outcome(analysis, case[1]), case[3])

    def test_first_matching_rule_wins(self):
        logic = LogicManager(Settings(env={}))
        analysis = self.make_analysis("negative", ["stress"])
        self.assertEqual(logic.rules_outcome(analysis, 1), "check_in")

    def test_ai_accept_cannot_lower_a_flag(self):
        logic = LogicManager(Settings(env={}))
        self.assertEqual(logic.more_serious("accept", "flag"), "flag")

    def test_score_adjustment(self):
        cases = [
            (3, "negative", 2),
            (1, "negative", 1),
            (2, "positive", 3),
            (4, "positive", 4),
            (3, "neutral", 3),
            (5, "negative", 4),
            (3, "positive", 4),
        ]
        logic = LogicManager(Settings(env={}))
        for case in cases:
            with self.subTest(str(case)):
                self.assertEqual(logic.adjust_score(case[0], case[1]), case[2])

    def test_three_low_entries_make_a_streak(self):
        policy = SupportPolicy(Settings(env={}))
        records = [self.make_record(2), self.make_record(1), self.make_record(2)]
        self.assertTrue(policy.has_low_mood_streak(records))

    def test_a_low_score_is_never_all_clear(self):
        logic = LogicManager(Settings(env={}))
        outcome, score = logic.evaluate(
            self.make_entry(2), self.make_analysis("neutral"), Journal()
        )
        self.assertEqual((outcome, score), ("check_in", 2))

    def test_weekly_plan_is_the_last_seven_entries(self):
        logic = LogicManager(Settings(env={}))
        batch = logic.plan_weekly(self.dated(10))
        self.assertEqual(len(batch), 7)
        self.assertEqual(batch[0].date, "2026-10-04")
        self.assertEqual(batch[-1].date, "2026-10-10")

    def test_counts_average_and_range(self):
        analyser = HistoryAnalyser(Settings(env={}))
        summary = analyser.summarise(
            [
                self.make_record(2, "2026-10-20T10:00:00", "check_in"),
                self.make_record(4, "2026-10-21T10:00:00", "accept"),
                self.make_record(3, "2026-10-22T10:00:00", "flag"),
            ]
        )
        self.assertEqual(summary.count, 3)
        self.assertEqual(summary.average, 3)
        self.assertEqual(summary.low, 2)
        self.assertEqual(summary.high, 4)
        self.assertEqual(
            summary.outcome_counts, {"accept": 1, "check_in": 1, "flag": 1}
        )

    def test_the_two_weeks_are_split_correctly(self):
        analyser = HistoryAnalyser(Settings(env={}))
        items = [
            (2, "2026-10-10T10:00:00"),
            (2, "2026-10-16T23:00:00"),
            (4, "2026-10-17T00:00:00"),
            (5, "2026-10-23T23:00:00"),
            (3, "2026-10-09T10:00:00"),
            (3, "2026-10-24T10:00:00"),
        ]
        records = []
        for item in items:
            records.append(self.make_record(item[0], item[1]))
        current, previous, direction = analyser.compare_weeks(
            Journal(records), date(2026, 10, 23)
        )
        self.assertEqual(previous.count, 2)
        self.assertEqual(current.count, 2)
        self.assertEqual(previous.average, 2)
        self.assertEqual(current.average, 4.5)
        self.assertEqual(current.label, "This week")
        self.assertEqual(previous.label, "Previous week")

    def test_a_good_reply_becomes_an_analysis(self):
        client = FakeAIClient(
            [self.good_reply("negative", "check_in", ["work", "stress"])]
        )
        ai = AIManager(client, QuestionBank(), Settings(env={}))
        analysis = ai.enrich(self.make_entry())
        self.assertEqual(analysis.sentiment, "negative")
        self.assertEqual(analysis.themes, ["work", "stress"])
        self.assertTrue(analysis.was_analysed())
        self.assertEqual(client.calls, 1)
        self.assertEqual(ai.warnings, [])

    def test_a_malformed_reply_is_retried_once(self):
        client = FakeAIClient(["not json at all", self.good_reply("positive")])
        ai = AIManager(client, QuestionBank(), Settings(env={}))
        analysis = ai.enrich(self.make_entry())
        self.assertEqual(analysis.sentiment, "positive")
        self.assertEqual(client.calls, 2)
        self.assertEqual(len(ai.warnings), 1)

    def test_two_bad_replies_fall_back_to_neutral(self):
        client = FakeAIClient(["nope"])
        ai = AIManager(client, QuestionBank(), Settings(env={}))
        analysis = ai.enrich(self.make_entry())
        self.assertEqual(client.calls, 2)
        self.assertFalse(analysis.was_analysed())
        self.assertEqual(analysis.recommended_outcome, "accept")
        self.assertIn("Using fallback, AI could not process this entry", ai.warnings)

    def test_a_reply_with_a_bad_schema_is_rejected(self):
        validator = ResponseValidator.for_entry()
        self.assertTrue(validator.validate(json.loads(self.good_reply())))
        broken = []
        for field, value in (
            ("sentiment", "happy"),
            ("recommended_outcome", "banana"),
            ("themes", "work"),
            ("reflection", 5),
        ):
            data = json.loads(self.good_reply())
            data[field] = value
            broken.append(data)
        missing = json.loads(self.good_reply())
        del missing["sentiment"]
        broken.append(missing)
        for data in broken:
            with self.subTest(str(data)[:40]):
                self.assertFalse(validator.validate(data))
        self.assertFalse(
            ResponseValidator.for_weekly().validate({"summary": "only one key"})
        )
        client = FakeAIClient([json.dumps({"sentiment": "happy"})])
        ai = AIManager(client, QuestionBank(), Settings(env={}))
        self.assertFalse(ai.enrich(self.make_entry()).was_analysed())
        self.assertEqual(client.calls, 2)

    def test_a_connection_error_is_not_retried(self):
        client = FakeAIClient([AIError("no network")])
        ai = AIManager(client, QuestionBank(), Settings(env={}))
        analysis = ai.enrich(self.make_entry())
        self.assertEqual(client.calls, 1)
        self.assertFalse(analysis.was_analysed())
        self.assertIn("AI error: no network, attempt 1", ai.warnings)

    def test_a_good_reply_comes_back_as_a_dictionary(self):
        client = FakeAIClient([self.weekly_reply()])
        ai = AIManager(client, QuestionBank(), Settings(env={}))
        result = ai.weekly_synthesis(
            [self.make_record(3), self.make_record(4), self.make_record(2)], "flat"
        )
        self.assertEqual(result["carry_forward"], "Evenings were calmer.")

    def test_liskov_any_ai_client_can_stand_in_for_another(self):
        self.assertTrue(issubclass(GeminiClient, AIClient))
        for replies in (
            [self.good_reply("positive")],
            [self.good_reply("positive", "accept", ["home"])],
        ):
            with self.subTest(str(replies)):
                client = FakeAIClient(replies)
                self.assertIsInstance(client, AIClient)
                ai = AIManager(client, QuestionBank(), Settings(env={}))
                self.assertEqual(ai.enrich(self.make_entry()).sentiment, "positive") 

    def test_mood_is_a_choice_of_one_to_five(self):
        self.check_validator(
            ChoiceValidator("12345", "Enter a number from 1 to 5."),
            ["1", "3", "5"],
            ["0", "6", "", "x", "3.5", "-1", "²"],
        )

    def test_date(self):
        self.check_validator(
            DateValidator(),
            ["2026-10-23"],
            ["", "23/10/2026", "2026-13-01", "today", "2026-1-1"],
        )

if __name__ == "__main__":
    unittest.main()
