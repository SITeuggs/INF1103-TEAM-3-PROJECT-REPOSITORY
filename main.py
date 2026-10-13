import random
from datetime import datetime, timedelta

from data_manager import load_entries, save_entry, load_config, save_config
from ai_manager import enrich, weekly_synthesis
from logic_manager import (
    evaluate, build_row, needs_support_info, recent_entries,
    sort_by_time, entries_since, mood_trajectory,
    WEEKLY_LIMIT, WEEKLY_DAYS, MIN_ENTRIES_FOR_REVIEW, SUPPORT_CONTACTS,
)
from io_manager import (
    ask,
    collect_note, collect_mood, collect_trigger, collect_followup,
    collect_clarity, collect_clarity_followup, collect_close, collect_mode,
    show_entry, show_entries, show_weekly, show_weekly_snapshot,
    show_support,
)

ID_CHARACTERS = "0123456789abcdef"


def valid_menu(x):
    """Check the input is one of the menu choices."""
    return x in ("1", "2", "3", "4", "q")


def make_entry_id():
    """Build a random 8-character id such as '3fa94c1e'."""
    entry_id = ""
    for i in range(8):
        entry_id = entry_id + ID_CHARACTERS[random.randint(0, 15)]
    return entry_id


def make_timestamp():
    """Build a timestamp like '2026-10-02T15:52:10'."""
    # str(datetime.now()) looks like '2026-10-02 15:52:10.123456'
    now_text = str(datetime.now())
    return now_text[:10] + "T" + now_text[11:19]


def greeting_for(hour):
    """Turn the hour of the day into morning, afternoon or evening."""
    if hour < 12:
        return "morning"
    if hour < 18:
        return "afternoon"
    return "evening"