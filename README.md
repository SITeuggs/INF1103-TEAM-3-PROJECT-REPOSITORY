# MIRA · AI Reflection Companion

A command-line mood reflection journal. You answer seven questions about your day,
an AI (Google Gemini) reads what you wrote, and a set of rules in the program decides
whether the entry is fine or worth a second look. Entries are saved to a Google Sheet.

## Features

- **Log a moment**: seven adaptive questions. The follow-up questions change
  depending on your mood rating and your earlier answers.
- **View entries**: a table of your most recent entries.
- **Weekly review**: looks at the last 7 days and asks the AI for one summary
  across them. With fewer than 3 entries it shows a calculated snapshot instead,
  so it never invents a pattern out of two data points.
- **Support**: shows support contacts. These also appear automatically after a low-mood entry.

## Before you start

You need:
- A **Gemini API key**. Get one free at https://aistudio.google.com/apikey
- **Python 3.11+** and **Docker Desktop**

### 1. Create a `.env` file

In the project folder, create a file named `.env` (no other name, no `.txt` ending)
containing one line:

```
GEMINI_KEY=paste-your-key-here
```

> ⚠️ Never commit `.env` or share it. It's listed in `.gitignore` so git skips it.
> If your key ever leaks, delete it in Google AI Studio and make a new one.

## Running it

### Option A: Python

```bash
pip install -r requirements.txt
python main.py
```

### Option B: Docker

```bash
docker build -t mira .
docker run -it --rm --env-file .env -v "${PWD}/data:/app/data" mira
```

- `-it` lets you type answers into the program.
- `--env-file .env` passes your API key in when the container starts. It is
  never built into the image.
- `-v .../data:/app/data` saves `config.json` (your name) to the `data` folder on
  your computer, so the app remembers you between runs.

## First run

Mira asks for your name once and saves it to `config.json`. To use a different
name, delete `config.json` (or `data/config.json` with Docker).

## The files

| File | Description |
|---|---|
| `main.py` | The menu and the order things happen in. |
| `io_manager.py` | Every `input()` and every `print()`. Decides nothing. |
| `logic_manager.py` | Question data, the scoring rules, the row builder. No I/O at all. |
| `ai_manager.py` | Everything that talks to Gemini, including validating what comes back. |
| `data_manager.py` | Reading and writing Google Sheets and the local config file. |
| `requirements.txt` | Python packages the project needs. |
| `Dockerfile` | Builds the app into a container. |
| `.env` | Your Gemini API key. You create this yourself; it is not in the repo. |

## Troubleshooting

| Problem | Fix |
|---|---|
| `Using fallback, AI could not process this entry` | Check `.env` exists, the variable is named `GEMINI_KEY`, and the key is valid. |
| `Could not reach Google Sheets` | Check your internet connection. The entry is kept until you quit, but it isn't saved to the sheet. |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again. |
| Docker: can't type answers | Make sure you used `docker run -it`. |