# Handles all user input and output.
# Nothing in this file decides anything, it only asks and shows.

from logic_manager import (
    MOOD_SCALE, TRIGGERS, FOLLOWUPS, CLARITY_OPTIONS,
    CLARITY_FOLLOWUPS, CLOSE_PROMPTS, MODES, OUTCOME_LABELS,
    MIN_ENTRIES_FOR_REVIEW,
    mood_band, get_value, join_with, mood_range, average_mood,
)

WIDTH = 58

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]



def pad_right(text, width):
    """Add spaces after text until it is width characters long."""
    text = str(text)
    return text + " " * (width - len(text))


def pad_left(text, width):
    """Add spaces before text until it is width characters long."""
    text = str(text)
    return " " * (width - len(text)) + text


def wrap_text(text, width):
    """Split a paragraph into a list of lines no longer than width."""
    lines = []
    current = ""
    for word in str(text).split():
        if current == "":
            current = word
        elif len(current) + 1 + len(word) <= width:
            current = current + " " + word
        else:
            lines.append(current)
            current = word
    if current != "":
        lines.append(current)
    return lines


def format_stamp(timestamp):
    """Turn '2026-10-02T15:52:10' into '02 OCT 2026 · 15:52'."""
    timestamp = str(timestamp)
    month = timestamp[5:7]
    if len(timestamp) >= 16 and month.isdigit():
        month_number = int(month)
        if month_number >= 1 and month_number <= 12:
            return (timestamp[8:10] + " " + MONTHS[month_number - 1] + " "
                    + timestamp[0:4] + " · " + timestamp[11:16])
    return timestamp[:16]



def valid_mood(x):
    """Check the input is a number from 1 to 5."""
    if not x.isdigit():
        return False
    number = int(x)
    return number >= 1 and number <= 5


def valid_abcd(x):
    """Check the input is A, B, C, or D."""
    return x.upper() in ("A", "B", "C", "D")


def valid_abc(x):
    """Check the input is A, B, or C."""
    return x.upper() in ("A", "B", "C")


def not_empty(x):
    """Check the input isn't blank."""
    return len(x) > 0



def ask(question, is_valid, error_msg):
    """
    Keep asking the same question until the answer passes the check.
    is_valid is one of the check functions above, passed in as an argument.
    """
    while True:
        raw = input("  " + question + "  > ").strip()
        if is_valid(raw):
            return raw
        print("  -> " + error_msg)