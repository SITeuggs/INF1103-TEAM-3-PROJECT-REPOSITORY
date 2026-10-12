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



        def collect_note():
    """Q1. The free-form note about the user's day."""
    print("\n  How's your day been? Tell me about it!")
    print("  Type 'done' on its own line to finish.\n")

    while True:
        lines = []
        while True:
            line = input("  | ")
            if line.strip().lower() == "done":
                break
            lines.append(line)

        text = join_with(lines, "\n").strip()
        if text:
            return text
        print("  -> Write at least a few words.")


def collect_mood():
    """Q2. The mood score from 1 to 5."""
    print("\n  How's your mood been today?\n")
    for i in range(1, 6):
        print("    " + str(i) + "  " + MOOD_SCALE[i]["emoji"]
              + "  " + MOOD_SCALE[i]["text"])
    print()

    mood = int(ask("Pick 1-5", valid_mood, "Enter a number from 1 to 5."))
    print("  -> " + MOOD_SCALE[mood]["emoji"] + "  " + MOOD_SCALE[mood]["text"])
    return mood


def collect_trigger(mood):
    """Q3a. What drove the mood. The options change with the mood band."""
    trigger = TRIGGERS[mood_band(mood)]
    options = trigger["options"]

    print("\n  " + trigger["prompt"] + "\n")
    for key in options.keys():
        print("    " + key + "  " + options[key])
    print()

    choice = ask("Pick A, B, C, or D", valid_abcd, "Enter A, B, C, or D.").upper()
    print("  -> " + options[choice])
    return choice, trigger["prompt"]


def collect_followup(mood, trigger_choice):
    """Q3b. An optional follow-up that depends on the trigger choice."""
    question = FOLLOWUPS[mood_band(mood)][trigger_choice]

    if question is None:
        print("\n  (No follow-up needed)")
        return "", ""

    print("\n  " + question)
    answer = input("  (Enter to skip, or type to elaborate)  > ").strip()

    if not answer:
        print("  -> Skipped")
    return answer, question


def collect_clarity():
    """Q4. How clearly the user can name what they're feeling."""
    print("\n  Do you understand what you're feeling right now?\n")
    for key in CLARITY_OPTIONS.keys():
        print("    " + key + "  " + CLARITY_OPTIONS[key])
    print()

    choice = ask("Pick A, B, or C", valid_abc, "Enter A, B, or C.").upper()
    print("  -> " + CLARITY_OPTIONS[choice])
    return choice


def collect_clarity_followup(mood, clarity):
    """Q4a. Follow-up that depends on both the clarity answer and the mood."""
    question = CLARITY_FOLLOWUPS[clarity][mood_band(mood)]

    print("\n  " + question)
    answer = ask("", not_empty, "Write at least a few words.")
    return answer, question


def collect_close(mood):
    """Q5. The closing question. Changes with the mood band."""
    question = CLOSE_PROMPTS[mood_band(mood)]

    print("\n  " + question)
    answer = ask("", not_empty, "Write at least a few words.")
    return answer, question


def collect_mode():
    """Q6. Which kind of response the user wants back."""
    print("\n  What would help most right now?\n")
    for key in MODES.keys():
        print("    " + key + "  " + MODES[key])
    print()

    choice = ask("Pick A, B, or C", valid_abc, "Enter A, B, or C.").upper()
    print("  -> " + MODES[choice])
    return choice
