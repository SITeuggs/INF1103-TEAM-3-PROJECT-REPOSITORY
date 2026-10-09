# ai_manager.py
# Handles all communication with the Gemini API.

import json
import logging

from google import genai

from logic_manager import (
    MOOD_SCALE, TRIGGERS, CLARITY_OPTIONS, MODES, mood_band,
    get_value, join_with,
)

# the SDK prints a warning about a feature we do not use, so quieten it
logging.getLogger("google_genai").setLevel(logging.ERROR)

#environmental variable for Gemini API Key
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()  

GEMINI_KEY = os.getenv("GEMINI_KEY")
gemini_client = genai.Client(api_key=GEMINI_KEY)
MODEL = "gemini-3.5-flash-lite"