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