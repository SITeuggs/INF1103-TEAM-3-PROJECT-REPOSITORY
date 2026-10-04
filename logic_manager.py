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
