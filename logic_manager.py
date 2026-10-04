# logic_manager.py
# Holds the question data, the scoring rules, and the row builder.
# No input() and no print() in this file, so the rules can be tested on their own.

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