# test_logic.py
# Checks every function in logic_manager.py using hardcoded sample data.
# Needs no internet, API key or Google Sheet. Run it with: python test_logic.py

import sys
import logic_manager

tally = {"passed": 0, "failed": 0}


def check(name, actual, expected):
    """Compare two values and print PASS or FAIL."""
    if actual == expected:
        tally["passed"] = tally["passed"] + 1
        print("  PASS  " + name)
    else:
        tally["failed"] = tally["failed"] + 1
        print("  FAIL  " + name)
        print("        expected: " + str(expected))
        print("        got:      " + str(actual))


def make_ai(sentiment, themes, outcome):
    """A sample AI reply. Only the fields the rules use are chosen."""
    return {
        "sentiment": sentiment, "emotions": ["tired", "worried"],
        "themes": themes, "congruence": "aligned", "congruence_note": "",
        "tag_ai": "work", "recommended_outcome": outcome,
        "reasoning": "sample", "reflection": "sample reflection",
        "reframe": "sample reframe",
    }


def make_record(mood):
    """A saved entry the AI analysed."""
    return {"mood": mood, "timestamp": "2026-10-01T10:00:00",
            "sentiment": "neutral", "reflection": "sample reflection"}


def low_records():
    """Three saved entries that are all low mood."""
    return [make_record(2), make_record(1), make_record(2)]


def test_apply_rules():
    print("\nOutcome rules")
    # each case is (sentiment, mood, themes, expected outcome)
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
    for case in cases:
        name = case[0] + ", mood " + str(case[1]) + ", " + str(case[2])
        check(name, logic_manager.apply_rules(case[0], case[1], case[2]),
              case[3])


def test_pick_more_serious():
    print("\nMore serious wins")
    check("rules beat AI accept",
          logic_manager.pick_more_serious("accept", "check_in"), "check_in")
    check("AI flag beats rules check_in",
          logic_manager.pick_more_serious("flag", "check_in"), "flag")
    check("AI accept cannot lower a flag",
          logic_manager.pick_more_serious("accept", "flag"), "flag")
    check("unknown AI outcome cannot win",
          logic_manager.pick_more_serious("banana", "accept"), "accept")


def test_adjust_score():
    print("\nScore adjustment")
    # each case is (mood, sentiment, expected score)
    cases = [(3, "negative", 2), (1, "negative", 1), (2, "positive", 3),
             (4, "positive", 4), (3, "neutral", 3)]
    for case in cases:
        name = "mood " + str(case[0]) + ", " + case[1]
        check(name, logic_manager.adjust_score(case[0], case[1]), case[2])


def test_support():
    print("\nStreak and support box")
    check("three low entries make a streak",
          logic_manager.has_low_mood_streak(low_records()), True)
    check("two entries are not enough",
          logic_manager.has_low_mood_streak(low_records()[:2]), False)

    mixed = [make_record(2), make_record(4), make_record(2)]
    check("one high entry breaks the streak",
          logic_manager.has_low_mood_streak(mixed), False)

    check("support shown at mood 1",
          logic_manager.needs_support_info(1, 3, "accept", []), True)
    check("support shown at score 2",
          logic_manager.needs_support_info(3, 2, "accept", []), True)
    check("support shown on flag",
          logic_manager.needs_support_info(4, 4, "flag", []), True)
    check("support shown after a streak",
          logic_manager.needs_support_info(4, 4, "accept", low_records()),
          True)
    check("support not shown on a normal day",
          logic_manager.needs_support_info(4, 4, "accept", []), False)


def test_evaluate():
    print("\nevaluate() with sample AI replies")

    # each case is (mood, sentiment, themes, AI outcome, expected outcome,
    #               expected score)
    cases = [
        (5, "positive", [], "accept", "accept", 5),
        (5, "negative", [], "accept", "check_in", 4),
        (2, "negative", ["work stress"], "accept", "flag", 2),
        (4, "positive", [], "flag", "flag", 4),
        (1, "positive", [], "accept", "check_in", 2),
        (3, "negative", [], "accept", "check_in", 2),
        (3, "neutral", [], "accept", "accept", 3),
        (3, "neutral", [3, None, "Study"], "accept", "accept", 3),
    ]
    for case in cases:
        ai = make_ai(case[1], case[2], case[3])
        outcome, score = logic_manager.evaluate({"mood": case[0]}, ai, [])
        name = "mood " + str(case[0]) + ", " + case[1] + ", " + str(case[2])
        check(name + ": outcome", outcome, case[4])
        check(name + ": score", score, case[5])

    outcome, score = logic_manager.evaluate(
        {"mood": 4}, make_ai("neutral", [], "accept"), low_records())
    check("streak raises accept to check_in", outcome, "check_in")

    outcome, score = logic_manager.evaluate({"mood": 3}, {}, [])
    check("empty AI reply does not crash", outcome, "accept")


def test_saved_entries():
    print("\nWorking with saved entries")
    fallback_row = {"mood": 3, "sentiment": "neutral", "reflection": ""}
    check("analysed entry counts",
          logic_manager.was_analysed(make_record(3)), True)
    check("fallback row does not count",
          logic_manager.was_analysed(fallback_row), False)

    rows = [make_record(1), fallback_row, make_record(2)]
    check("recent_entries drops fallback rows",
          len(logic_manager.recent_entries(rows, 10)), 2)

    first = make_record(1)
    first["timestamp"] = "2026-10-03T09:00:00"
    second = make_record(2)
    second["timestamp"] = "2026-10-01T09:00:00"
    ordered = logic_manager.sort_by_time([first, second])
    check("sort_by_time puts oldest first",
          logic_manager.mood_values(ordered), [2, 1])

    kept = logic_manager.entries_since([first, second], "2026-10-02")
    check("entries_since drops older entries",
          logic_manager.mood_values(kept), [1])


def test_helpers():
    print("\nSmall helpers")
    check("get_value finds a key",
          logic_manager.get_value({"a": 1}, "a", 0), 1)
    check("get_value uses the default",
          logic_manager.get_value({"a": 1}, "b", 0), 0)
    check("join_with joins with a separator",
          logic_manager.join_with(["a", "b", "c"], "|"), "a|b|c")
    check("join_with handles an empty list",
          logic_manager.join_with([], "|"), "")
    check("join_with turns numbers into text",
          logic_manager.join_with([1, 2], ", "), "1, 2")
    check("average of 1, 2, 3", logic_manager.average([1, 2, 3]), 2)

 
def test_mood_band():
    print("\nMood bands")
    cases = [(1, "low"), (2, "low"), (3, "neutral"), (4, "high"), (5, "high")]
    for case in cases:
        check("mood " + str(case[0]),
              logic_manager.mood_band(case[0]), case[1])


def test_mood_numbers():
    print("\nMood numbers")
    records = [make_record(2), make_record(4), make_record(3)]
    blank = make_record(3)
    blank["mood"] = ""

    check("entry_time reads the timestamp",
          logic_manager.entry_time(make_record(3)), "2026-10-01T10:00:00")
    check("mood_range gives low and high",
          logic_manager.mood_range(records), (2, 4))
    check("mood_range of nothing is 0, 0",
          logic_manager.mood_range([]), (0, 0))
    check("average_mood of 2, 4, 3",
          logic_manager.average_mood(records), 3)
    check("average_mood of nothing is 0",
          logic_manager.average_mood([]), 0)
    check("blank mood is skipped in the range",
          logic_manager.mood_range([make_record(2), blank]), (2, 2))


def test_trajectory():
    print("\nMood trajectory")
    # each case is (list of moods, expected trajectory)
    cases = [([3], "flat"), ([3, 3, 3, 3], "flat"), ([2, 3, 4], "rising"),
             ([5, 5, 2, 2], "falling"), ([1, 5, 1, 5], "volatile")]
    for case in cases:
        records = []
        for m in case[0]:
            records.append(make_record(m))
        check("moods " + str(case[0]),
              logic_manager.mood_trajectory(records), case[1])


def test_build_row():
    print("\nbuild_row()")
    entry = {
        "id": "3fa94c1e", "timestamp": "2026-10-02T15:52:10",
        "profile": "Test", "note": "Long day.", "mood": 2,
        "trigger_choice": "A", "trigger_prompt": "What pulled things down?",
        "followup_text": "Deadlines", "followup_q": "What keeps coming back?",
        "clarity": "B", "clarity_text": "Maybe stress", "clarity_q": "Guess?",
        "close_text": "Sleep early", "close_q": "What will you change?",
        "mode": "A",
    }
    ai = make_ai("negative", ["work stress"], "accept")
    outcome, score = logic_manager.evaluate(entry, ai, [])
    row = logic_manager.build_row(entry, ai, outcome, score)

    check("row has 31 columns", len(row), 31)
    check("row looks up the trigger label", row["trigger_label"],
          "An internal thought or worry")
    check("row joins emotions with pipes", row["emotions"], "tired|worried")
    check("row stores the outcome", row["outcome"], "flag")
