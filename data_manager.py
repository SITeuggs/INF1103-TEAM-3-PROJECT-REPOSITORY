# data_manager.py
# Handles reading and writing data to Google Sheets and local config.

import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

SHEET_URL = os.getenv("SHEET_URL")
CONFIG_FILE = os.getenv("CONFIG_FILE", "config.json")
TIMEOUT = 30

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

        # make sure mood and score come back as numbers, not text.
        # a bad cell only affects its own row, instead of losing every entry
        for entry in data:
            for key in ("mood", "score"):
                value = entry.get(key)
                if value is not None and value != "":
                    try:
                        entry[key] = int(value)
                    except ValueError:
                        entry[key] = 0

        return data

    except Exception as e:
        print(f"  (Could not load from Sheets: {e})")
        return []

def save_entry(row: dict) -> bool:
    """Save one entry row to Google Sheets. Returns True if it worked."""
    # turn every value into text before sending
    record = {}
    for key, value in row.items():
        record[key] = str(value)

    payload = {
        "headers": FIELDNAMES,
        "record": record,
    }

    try:
        resp = requests.post(SHEET_URL, json=payload,
                             allow_redirects=True, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"  (Could not save to Sheets: {e})")
        return False

    if resp.status_code != 200:
        return False

    try:
        result = resp.json()
        if result.get("status") == "ok":
            return True
        return False
    except ValueError:
        # got a 200 but not json — assume it went through
        return True

def load_config() -> dict:
    """Load the local config file, which stores the user's name."""
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict) -> None:
    """Save the local config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print(f"  (Failed to save config: {e})")
