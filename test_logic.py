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
