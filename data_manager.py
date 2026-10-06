# data_manager.py
# Handles reading and writing data to Google Sheets and local config.

import json
import os
import re

SHEET_URL = "https://script.google.com/macros/s/AKfycbxEk8gxLvjqRYBgTEMn5x2Faa_ihPWGDhT1FTurPxGgBp6AK8vbcPMT193Y9D0NcgKG/exec"
CONFIG_FILE = "config.json"

# column order for the Google Sheet — do not reorder these
FIELDNAMES = [
    "id", "timestamp", "profile",
    "note",
    "mood", "mood_label",
    "trigger_prompt", "trigger_choice", "trigger_label",
    "followup_prompt", "followup_text",
    "clarity_choice", "clarity_label",
    "clarity_prompt", "clarity_text",
    "close_prompt", "close_text",
    "mode_choice", "mode_label",
    "sentiment", "emotions", "themes",
    "congruence", "congruence_note",
    "tag_ai", "recommended_outcome", "reasoning",
    "reflection", "reframe",
    "outcome", "score",
]