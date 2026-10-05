# logic_manager.py
# Holds the question data, the scoring rules, and the row builder.

MOOD_SCALE = {
    1: {"emoji": "😔", "text": "I'm struggling — today took more than I had to give"},
    2: {"emoji": "😕", "text": "Not my best — something's been nagging at me"},
    3: {"emoji": "😐", "text": "Somewhere in the middle — nothing's pulling me up or down"},
    4: {"emoji": "🙂", "text": "I'm in a good place — things clicked more than usual"},
    5: {"emoji": "🌟", "text": "Really good — I'm feeling present and grounded"},
}

TRIGGERS = {
    "high": {
        "prompt": "What do you think made the difference today?",
        "options": {
            "A": "A win or milestone — something clicked",
            "B": "A meaningful interaction or connection",
            "C": "Physical state — good sleep, movement, energy",
            "D": "Nothing specific — just a good day",
        },
    },
    "low": {
        "prompt": "What do you think pulled things down?",
        "options": {
            "A": "An internal thought or worry",
            "B": "An external event or person",
            "C": "Physical state — poor sleep, fatigue, illness",
            "D": "Not sure — just feels off",
        },
    },
    "neutral": {
        "prompt": "Was there a specific driver behind that score?",
        "options": {
            "A": "A specific win or milestone",
            "B": "An internal thought or worry",
            "C": "An external event or person",
            "D": "Just physical state",
        },
    },
}

FOLLOWUPS = {
    "high": {
        "A": "What clicked?",
        "B": "Who was it with?",
        "C": "What felt different physically?",
        "D": None,
    },
    "low": {
        "A": "What's the thought that keeps coming back?",
        "B": "What happened, in a line?",
        "C": "What's your body telling you right now?",
        "D": "If you had to guess, what's underneath?",
    },
    "neutral": {
        "A": "Nice — what happened?",
        "B": "What's the thought that keeps coming back?",
        "C": "What happened, in a line?",
        "D": "What's your body telling you right now?",
    },
}

CLARITY_OPTIONS = {
    "A": "Yes — I can put it into words",
    "B": "Partly — I can feel it but can't quite explain it",
    "C": "Not really — it's kind of a blur",
}

CLARITY_FOLLOWUPS = {
    "A": {
        "high":    "What felt different about today compared to a normal day?",
        "low":     "What's one thing within your control right now?",
        "neutral": "What's one thing within your control right now?",
    },
    "B": {
        "high":    "If you had to take a guess, what would you call it?",
        "low":     "If you had to take a guess, what would you call it?",
        "neutral": "If you had to take a guess, what would you call it?",
    },
    "C": {
        "high":    "That's okay. What's one thing you do know for sure right now?",
        "low":     "That's okay. What's one thing you do know for sure right now?",
        "neutral": "That's okay. What's one thing you do know for sure right now?",
    },
}

CLOSE_PROMPTS = {
    "high":    "What's one thing from today you want to carry into tomorrow?",
    "low":     "What's one small thing you want to do differently tomorrow?",
    "neutral": "What's one thing you want to take away from today?",
}

MODES = {
    "A": "A straight, honest read",
    "B": "Celebrate it and lock it in",
    "C": "Somewhere to set it down",
}

OUTCOME_LABELS = {
    "accept":   "all clear",
    "flag":     "worth sitting with",
    "check_in": "worth a closer look",
}


SEVERITY = {"accept": 0, "check_in": 1, "flag": 2}


STRESS_THEMES = ("stress", "pressure", "overwhelm")

SUPPORT_CONTACTS = [
    {"name": "Samaritans of Singapore", "contact": "1767"},
    {"name": "SOS CareText (WhatsApp)", "contact": "9151 1767"},
    {"name": "SIT Counselling", "contact": "6592 2030"},
    {"name": "mindline.sg", "contact": "free, anonymous, online"},
]

WEEKLY_LIMIT = 7
WEEKLY_DAYS = 7

MIN_ENTRIES_FOR_REVIEW = 3

# ---------- small helpers ----------

def get_value(data, key, default):
    """Return data[key] if the key exists, otherwise return default.""" 
    if key in data.keys():
        return data[key]
    return default


def join_with(parts, separator):
    """Join a list of items into one string with separator in between."""
    text = ""
    for i in range(len(parts)):
        if i > 0:
            text = text + separator
        text = text + str(parts[i])
    return text


def average(numbers):
    """Work out the mean of a list of numbers."""
    total = 0
    for n in numbers:
        total = total + n
    return total / len(numbers)

# ---------- rules ----------

def mood_band(mood):
    """Turn a 1-5 mood score into high, neutral or low."""
    if mood >= 4:
        return "high"
    if mood <= 2:
        return "low"
    return "neutral"


def apply_rules(sentiment, mood, themes):
    """
    Work out the outcome from our own rules only, ignoring the AI's pick.
    This is what keeps the app working even when the AI is wrong.
    """
    has_stress_theme = False
    for theme in themes:
        if theme in STRESS_THEMES:
            has_stress_theme = True
            break

    if sentiment == "negative" and mood >= 4:
        return "check_in"
    elif sentiment == "positive" and mood <= 2:
        return "check_in"
    elif mood == 1:
        return "check_in"
    elif has_stress_theme and mood <= 2:
        return "flag"
    else:
        return "accept"


def pick_more_serious(ai_outcome, rules_outcome):
    """Return whichever outcome is more serious, so neither side can downgrade the other."""
    ai_severity = get_value(SEVERITY, ai_outcome, 0)
    rules_severity = SEVERITY[rules_outcome]

    if ai_severity > rules_severity:
        return ai_outcome
    return rules_outcome


def adjust_score(mood, sentiment):
    """Move the score by one when the writing disagrees with the rating."""
    score = mood

    if sentiment == "negative" and mood >= 3:
        score = score - 1
        if score < 1:
            score = 1
    elif sentiment == "positive" and mood <= 3:
        score = score + 1
        if score > 5:
            score = 5

    return score


def has_low_mood_streak(records):
    """
    Check whether the last three entries were all low mood.
    Three entries, not three days: logging twice in one evening counts
    as two. Grouping by date would be the next improvement.
    """
    last_three = records[-3:]
    if len(last_three) < 3:
        return False

    for r in last_three:
        past_mood = get_value(r, "mood", 3)
        if not past_mood:
            past_mood = 3
        if int(past_mood) > 2:
            return False

    return True


def needs_support_info(mood, score, outcome, records):
    """
    Decide whether to show the support contacts after an entry.
    Fires on the lowest mood, a score of 2 or below, a serious
    outcome, or three low entries before this one.
    records does not include the entry being logged, so this rule
    is about the run leading up to today rather than today itself.
    """
    if mood == 1:
        return True
    if score <= 2:
        return True
    if get_value(SEVERITY, outcome, 0) >= 2:
        return True
    if has_low_mood_streak(records):
        return True
    return False


def was_analysed(record):
    """
    True when the AI actually produced a reading for this entry.
    A fallback row still has a sentiment but no reflection, so the
    reflection is what tells the two apart.
    """
    if not get_value(record, "sentiment", ""):
        return False
    if not get_value(record, "reflection", ""):
        return False
    return True

def recent_entries(records, limit):
    """The most recent entries the AI actually analysed."""
    analysed = []
    for r in records:
        if was_analysed(r):
            analysed.append(r)
    return analysed[-limit:]