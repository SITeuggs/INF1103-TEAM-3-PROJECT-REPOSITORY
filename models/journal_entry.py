import random
from datetime import datetime

class JournalEntry:
    ID_CHARACTERS = "0123456789abcdef"

    def __init__(self, entry_id, timestamp, profile, note, mood,
                 trigger_choice, trigger_prompt, followup_text, followup_q,
                 clarity, clarity_text, clarity_q, close_text, close_q, mode):
        self._id = entry_id
        self._timestamp = timestamp
        self._profile = profile
        self._note = note
        self._mood = mood
        self._trigger_choice = trigger_choice
        self._trigger_prompt = trigger_prompt
        self._followup_text = followup_text
        self._followup_q = followup_q
        self._clarity = clarity
        self._clarity_text = clarity_text
        self._clarity_q = clarity_q
        self._close_text = close_text
        self._close_q = close_q
        self._mode = mode

    @staticmethod
    def make_id():
        entry_id = ""
        for i in range(8):
            entry_id = entry_id + random.choice(JournalEntry.ID_CHARACTERS)
        return entry_id

    @staticmethod
    def make_timestamp(now=None):
        if now is None:
            now = datetime.now()
        now_text = str(now)
        return now_text[:10] + "T" + now_text[11:19]

    def with_answers(self, answers):
        """A new entry with every answer replaced; id, date and profile stay."""
        return JournalEntry(
            self._id,
            self._timestamp,
            self._profile,
            answers["note"],
            answers["mood"],
            answers["trigger_choice"],
            answers["trigger_prompt"],
            answers["followup_text"],
            answers["followup_q"],
            answers["clarity"],
            answers["clarity_text"],
            answers["clarity_q"],
            answers["close_text"],
            answers["close_q"],
            answers["mode"],
        )

    @classmethod
    def from_answers(cls, profile, answers, now=None):
        return cls(
            JournalEntry.make_id(),
            JournalEntry.make_timestamp(now),
            profile,
            answers["note"],
            answers["mood"],
            answers["trigger_choice"],
            answers["trigger_prompt"],
            answers["followup_text"],
            answers["followup_q"],
            answers["clarity"],
            answers["clarity_text"],
            answers["clarity_q"],
            answers["close_text"],
            answers["close_q"],
            answers["mode"],
        )

    @property
    def id(self):
        return self._id

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def profile(self):
        return self._profile

    @property
    def note(self):
        return self._note

    @property
    def mood(self):
        return self._mood

    @property
    def trigger_choice(self):
        return self._trigger_choice

    @property
    def trigger_prompt(self):
        return self._trigger_prompt

    @property
    def followup_text(self):
        return self._followup_text

    @property
    def followup_q(self):
        return self._followup_q

    @property
    def clarity(self):
        return self._clarity

    @property
    def clarity_text(self):
        return self._clarity_text

    @property
    def clarity_q(self):
        return self._clarity_q

    @property
    def close_text(self):
        return self._close_text

    @property
    def close_q(self):
        return self._close_q

    @property
    def mode(self):
        return self._mode
