from datetime import datetime
from ai_manager import AIManager
from ai_parts.gemini_client import GeminiClient
from data_manager import DataManager
from data_parts.config_store import ConfigStore
from data_parts.sqlite_storage import SQLiteStorage
from errors.storage_error import StorageError
from io_manager import IOManager
from logic_manager import LogicManager
from logic_parts.question_bank import QuestionBank
from models.journal_entry import JournalEntry
from settings import Settings

class JournalApp:
    def __init__(self, io, ai, logic, data, clock=None,
                 sample_file="sample_entries.json", auto_samples=False):
        self._io = io
        self._ai = ai
        self._logic = logic
        self._data = data
        self._clock = clock
        self._sample_file = sample_file
        self._auto_samples = auto_samples
        self._name = "friend"

    @classmethod
    def from_settings(cls, settings):
        bank = QuestionBank()
        client = GeminiClient(settings.gemini_key, settings.MODEL,
                              settings.AI_TIMEOUT_SECONDS)
        ai = AIManager(client, bank, settings)
        storage = SQLiteStorage(settings.database_file)
        data = DataManager(storage, ConfigStore(settings.config_file))
        return cls(IOManager(bank, settings), ai,
                   LogicManager(settings, bank), data,
                   sample_file=settings.sample_file, auto_samples=True)

    def _now(self):
        if self._clock is None:
            return datetime.now()
        return self._clock()

    @staticmethod
    def greeting_for(hour):
        if hour < 12:
            return "morning"
        if hour < 18:
            return "afternoon"
        return "evening"

    def _show_ai_warnings(self):
        for warning in self._ai.warnings:
            self._io.show_notice(warning)

    def _get_name(self):
        saved = self._data.get_profile()
        if saved is not None:
            return saved
        name = self._io.ask_name()
        if not name:
            name = "friend"
        try:
            self._data.set_profile(name)
        except StorageError as error:
            self._io.show_notice(str(error))
        return name

    def _start(self):
        self._name = self._get_name()
        self._io.show("\n  MIRA  .  a quiet place to reflect")
        self._io.show("  Loading your entries...")
        try:
            count = self._data.load()
        except StorageError as error:
            count = 0
            self._io.show_notice(str(error))
            self._io.show_notice("Starting with no history. New entries are "
                                 "kept only until you close the app.")
        if count == 0 and self._auto_samples and not self._data.samples_were_loaded():
            self._load_first_run_samples()
            count = self._data.journal.count()
        greeting = JournalApp.greeting_for(self._now().hour)
        self._io.show("  Good " + greeting + ", " + self._name + ". "
                      + str(count) + " entries loaded.\n")
        if count == 0:
            self._io.show("  Your journal is empty. Choose 1 to log your first "
                          "entry.\n")

    def _load_first_run_samples(self):
        try:
            self._data.load_samples(self._sample_file, self._now().date())
            self._data.mark_samples_loaded()
        except StorageError as error:
            self._io.show_notice(str(error))
            return False
        return True

    def log_entry(self):
        answers = self._io.collect_answers()
        entry = JournalEntry.from_answers(self._name, answers, self._now())
        self._io.show("\n  ... analysing your note\n")
        analysis = self._ai.enrich(entry)
        self._show_ai_warnings()
        journal = self._data.journal
        outcome, score = self._logic.evaluate(entry, analysis, journal)
        record = self._logic.build_record(entry, analysis, outcome, score)
        self._io.show_entry(record)
        if self._logic.needs_support(record, journal):
            self._io.show_support(self._logic.question_bank.support_contacts())
        if self._data.add_record(record):
            self._io.show(" ✓ Logged to " + self._data.storage_name + " · "
                          + str(self._data.journal.count()) + " entries total\n")
        else:
            self._io.show_notice(self._data.last_error)
            self._io.show(" ⚠ Could not save this entry. "
                          "It is only kept until you close MIRA.\n")

    def view_entries(self):
        self._io.show_entries(self._data.journal.records)

    def weekly_review(self):
        batch = self._logic.plan_weekly(self._data.journal)
        trajectory = self._logic.trajectory(batch)
        if len(batch) < self._logic.minimum_for_review:
            low, high = self._logic.mood_range(batch)
            mean = self._logic.average_mood(batch)
            self._io.show_weekly_snapshot(len(batch), trajectory, low, high, mean)
            return
        self._io.show("\n  ... generating your weekly review\n")
        result = self._ai.weekly_synthesis(batch, trajectory)
        self._show_ai_warnings()
        if result:
            self._io.show_weekly(result, len(batch), trajectory)
        else:
            self._io.show("  Could not generate weekly review.\n")

    def show_support(self):
        self._io.show_support(self._logic.question_bank.support_contacts())

    def history(self):
        current, previous, direction = self._logic.compare_weeks(
            self._data.journal, self._now().date())
        self._io.show_comparison(current, previous, direction)
        record_filter = self._io.ask_filter()
        matches = self._data.query(record_filter)
        if matches:
            self._io.show_filter_summary(self._logic.summarise_records(matches))
        self._io.show_entries(matches, "No entries match that filter.")

    def edit_entry(self):
        records = self._data.journal.records
        self._io.show_entries(records)
        if not records:
            return
        entry_id = self._io.ask_entry_id("edit")
        record = self._data.find_record(entry_id)
        if record is None:
            self._io.show("\n  No entry with that id.\n")
            return
        self._io.show_current_note(record)
        self._io.show("\n  Answer the questions again to replace this entry.")
        answers = self._io.collect_answers()
        entry = record.entry.with_answers(answers)
        self._io.show("\n  ... analysing your new answers\n")
        analysis = self._ai.enrich(entry)
        self._show_ai_warnings()
        earlier = self._data.journal.before(record.timestamp)
        outcome, score = self._logic.evaluate(entry, analysis, earlier)
        updated = self._logic.build_record(entry, analysis, outcome, score)
        self._io.show_entry(updated)
        if self._logic.needs_support(updated, earlier):
            self._io.show_support(self._logic.question_bank.support_contacts())
        if not self._io.ask_confirm("Replace the old version with this?"):
            self._io.show("\n  Kept the old version.\n")
            return
        try:
            found = self._data.update_record(updated)
        except StorageError as error:
            self._io.show_notice(str(error))
            self._io.show(" ⚠ Could not save the change.\n")
            return
        if found:
            self._io.show(" ✓ Updated entry " + entry_id + "\n")
        else:
            self._io.show("\n  No entry with that id.\n")

    def delete_entry(self):
        records = self._data.journal.records
        self._io.show_entries(records)
        if not records:
            return
        entry_id = self._io.ask_entry_id("delete")
        record = self._data.find_record(entry_id)
        if record is None:
            self._io.show("\n  No entry with that id.\n")
            return
        self._io.show_current_note(record)
        if not self._io.ask_confirm("Delete this entry for good?"):
            self._io.show("\n  Kept it.\n")
            return
        try:
            self._data.remove_record(entry_id)
        except StorageError as error:
            self._io.show_notice(str(error))
            return
        self._io.show("\n  Deleted entry " + entry_id + ".\n")

    def _menu_loop(self):
        while True:
            choice = self._io.ask_menu()
            if choice == "q":
                break
            elif choice == "2":
                self.view_entries()
            elif choice == "3":
                self.weekly_review()
            elif choice == "4":
                self.show_support()
            elif choice == "5":
                self.history()
            elif choice == "6":
                self.edit_entry()
            elif choice == "7":
                self.delete_entry()
            else:
                self.log_entry()

    def run(self):
        try:
            self._start()
            self._menu_loop()
        except (KeyboardInterrupt, EOFError):
            self._io.show("")
        self._io.show("\n  Take care, " + self._name + ".\n")
if __name__ == "__main__":
    JournalApp.from_settings(Settings()).run()
