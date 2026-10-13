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

def log_entry(name, records):
    """
    Run the whole flow for one entry:
    ask the questions, send them to the AI, apply the rules, then save.
    """
    note = collect_note()
    mood = collect_mood()
    trigger_choice, trigger_question = collect_trigger(mood)
    followup_text, followup_q = collect_followup(mood, trigger_choice)
    clarity = collect_clarity()
    clarity_text, clarity_q = collect_clarity_followup(mood, clarity)
    close_text, close_q = collect_close(mood)
    mode = collect_mode()

    entry = {
        "id":             make_entry_id(),
        "timestamp":      make_timestamp(),
        "profile":        name,
        "note":           note,
        "mood":           mood,
        "trigger_choice": trigger_choice,
        "trigger_prompt": trigger_question,
        "followup_text":  followup_text,
        "followup_q":     followup_q,
        "clarity":        clarity,
        "clarity_text":   clarity_text,
        "clarity_q":      clarity_q,
        "close_text":     close_text,
        "close_q":        close_q,
        "mode":           mode,
    }

    print("\n  ... analysing your note\n")

    ai = enrich(entry)
    outcome, score = evaluate(entry, ai, records)
    row = build_row(entry, ai, outcome, score)
    show_entry(row)

    if needs_support_info(mood, score, outcome, records):
        show_support(SUPPORT_CONTACTS)

    records.append(row)

    if save_entry(row):
        print(" ✓ Logged to Google Sheets · " + str(len(records)) + " entries total\n")
    else:
        print(" ⚠ Could not reach Google Sheets."
              " This entry is only kept until you close Mira.\n")


def week_cutoff():
    """
    The first date in the window, as text like '2026-09-27'.
    Minus one, because entries_since keeps the cutoff day itself, so
    today plus the six days before it is WEEKLY_DAYS in total.
    """
    return str(datetime.now() - timedelta(days=WEEKLY_DAYS - 1))[:10]

def weekly_review(records):
    """
    Show the weekly review.
    Prefers entries from the last 7 days. If there are too few, it looks
    further back and says so. If there are still too few, it shows the
    calculated snapshot instead of inventing patterns.
    """
    ordered = sort_by_time(records)
    this_week = entries_since(ordered, week_cutoff())

    widened = False
    if len(this_week) >= MIN_ENTRIES_FOR_REVIEW:
        batch = this_week[-WEEKLY_LIMIT:]
    else:
        batch = recent_entries(ordered, WEEKLY_LIMIT)
        widened = True

    trajectory = mood_trajectory(batch)

    if len(batch) < MIN_ENTRIES_FOR_REVIEW:
        show_weekly_snapshot(batch, trajectory)
        return

    if widened:
        print("\n  (Only " + str(len(this_week)) + " entries in the last "
              + str(WEEKLY_DAYS) + " days, so this looks further back.)")

    print("\n  ... generating your weekly review\n")
    result = weekly_synthesis(batch, trajectory)

    if result:
        result["mood_trajectory"] = trajectory
        show_weekly(result, len(batch))
    else:
        print("  Could not generate weekly review.\n")

def get_name():
    """Read the user's name from the config file, asking for it the first time."""
    config = load_config()

    if "profile" in config.keys():
        return config["profile"]

    name = input("\n  Welcome to Mira! What's your name?  > ").strip()
    if not name:
        name = "friend"
    config["profile"] = name
    save_config(config)
    return name
