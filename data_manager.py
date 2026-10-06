# data_manager.py
# Handles reading and writing data to Google Sheets and local config.

import json
import os
import re

import requests

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

def load_entries() -> list:
    """Read all saved entries back from Google Sheets."""
    try:
        resp = requests.get(SHEET_URL, allow_redirects=True, timeout=TIMEOUT)
        text = resp.text.strip()

        # apps script sometimes answers with an html page holding the real link
        if text.startswith("<!"):
            match = re.search(r'href="([^"]+)"', text)
            if match:
                real_url = match.group(1)
                text = requests.get(real_url, timeout=TIMEOUT).text.strip()

        data = json.loads(text)

        # the sheet can send back an error message instead of rows
        if isinstance(data, dict) and data.get("error"):
            print(f"  (Sheets error: {data['error']})")
            return []

        # make sure mood and score come back as numbers, not text
        for entry in data:
            for key in ("mood", "score"):
                value = entry.get(key)
                if value is not None and value != "":
                    entry[key] = int(value)

        return data

    except Exception as e:
        print(f"  (Could not load from Sheets: {e})")
        return []