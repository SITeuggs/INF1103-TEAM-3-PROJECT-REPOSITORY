from settings import Settings
from io_parts.choice_validator import ChoiceValidator
from io_parts.non_empty_validator import NonEmptyValidator
from settings import Settings

class IOManager:
    WIDTH = 58
    MENU_CHOICES = ("1", "2", "3", "4", "q")
    MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    
    def __init__(self, question_bank, settings=None, read=None, write=None):
        if settings is None:
            settings = Settings(env={})
        self._bank = question_bank
        self._settings = settings
        self._read = read if read is not None else input
        self._write = write if write is not None else print

    @staticmethod
    def pad_right(text, width):
        text = str(text)
        return text + " " * (width - len(text))

    @staticmethod
    def pad_left(text, width):
        text = str(text)
        return " " * (width - len(text)) + text

    @staticmethod
    def wrap_text(text, width):
        lines = []
        current = ""
        for word in str(text).split():
            if current == "":
                current = word
            elif len(current) + 1 + len(word) <= width:
                current = current + " " + word
            else:
                lines.append(current)
                current = word
        if current != "":
            lines.append(current)
        return lines

    @staticmethod
    def format_stamp(timestamp):
        timestamp = str(timestamp)
        month = timestamp[5:7]
        if len(timestamp) >= 16 and month.isdigit():
            month_number = int(month)
            if month_number >= 1 and month_number <= 12:
                return (timestamp[8:10] + " "
                        + IOManager.MONTHS[month_number - 1] + " "
                        + timestamp[0:4] + " · " + timestamp[11:16])
        return timestamp[:16]
    
    def ask(self, question, validator):
        while True:
            raw = self._read("  " + question + "  > ").strip()
            if raw == "" and validator.allow_blank:
                return raw
            if validator.is_valid(raw):
                return raw
            self._write("  -> " + validator.error_message)

    def ask_menu(self):
        self._write("  [1] Log a moment    [2] View entries    [3] Weekly review")
        self._write("  [4] Get support     [q] Quit")
        choice = self.ask("", ChoiceValidator(
            IOManager.MENU_CHOICES, "Pick 1, 2, 3, 4, or q."))
        return choice.lower()

    def ask_name(self):
        name = self._read("\n  Welcome to MIRA! What's your name?  > ").strip()
        return name

    def collect_note(self):
        self._write("\n  How's your day been? Tell me about it!")
        self._write("  Type 'done' on its own line to finish.\n")
        while True:
            lines = []
            while True:
                line = self._read("  | ")
                if line.strip().lower() == "done":
                    break
                lines.append(line)
            text = "\n".join(lines).strip()
            if text:
                return text
            self._write("  -> Write at least a few words.")

    def collect_mood(self):
        self._write("\n  How's your mood been today?\n")
        for i in range(1, 6):
            self._write("    " + str(i) + "  " + self._bank.mood_emoji(i)
                        + "  " + self._bank.mood_text(i))
        self._write("")
        mood = int(self.ask("Pick 1-5", ChoiceValidator("12345", "Enter a number from 1 to 5.")))
        self._write("  -> " + self._bank.mood_emoji(mood) + "  "
                    + self._bank.mood_text(mood))
        return mood

    def collect_trigger(self, mood):
        options = self._bank.trigger_options(mood)
        prompt = self._bank.trigger_prompt(mood)
        self._write("\n  " + prompt + "\n")
        for key in options.keys():
            self._write("    " + key + "  " + options[key])
        self._write("")
        choice = self.ask("Pick A, B, C, or D",
                          ChoiceValidator("ABCD", "Enter A, B, C, or D.")).upper()
        self._write("  -> " + options[choice])
        return choice, prompt

    def collect_followup(self, mood, trigger_choice):
        question = self._bank.followup_question(mood, trigger_choice)
        if question is None:
            self._write("\n  (No follow-up needed)")
            return "", ""
        self._write("\n  " + question)
        answer = self._read("  (Enter to skip, or type to elaborate)  > ").strip()
        if not answer:
            self._write("  -> Skipped")
        return answer, question

    def collect_clarity(self):
        options = self._bank.clarity_options()
        self._write("\n  Do you understand what you're feeling right now?\n")
        for key in options.keys():
            self._write("    " + key + "  " + options[key])
        self._write("")
        choice = self.ask("Pick A, B, or C",
                          ChoiceValidator("ABC", "Enter A, B, or C.")).upper()
        self._write("  -> " + options[choice])
        return choice

    def collect_clarity_followup(self, mood, clarity):
        question = self._bank.clarity_question(clarity, mood)
        self._write("\n  " + question)
        answer = self.ask("", NonEmptyValidator())
        return answer, question

    def collect_close(self, mood):
        question = self._bank.close_prompt(mood)
        self._write("\n  " + question)
        answer = self.ask("", NonEmptyValidator())
        return answer, question

    def collect_mode(self):
        modes = self._bank.modes()
        self._write("\n  What would help most right now?\n")
        for key in modes.keys():
            self._write("    " + key + "  " + modes[key])
        self._write("")
        choice = self.ask("Pick A, B, or C",
                          ChoiceValidator("ABC", "Enter A, B, or C.")).upper()
        self._write("  -> " + modes[choice])
        return choice

    def collect_answers(self):
        note = self.collect_note()
        mood = self.collect_mood()
        trigger_choice, trigger_question = self.collect_trigger(mood)
        followup_text, followup_q = self.collect_followup(mood, trigger_choice)
        clarity = self.collect_clarity()
        clarity_text, clarity_q = self.collect_clarity_followup(mood, clarity)
        close_text, close_q = self.collect_close(mood)
        mode = self.collect_mode()
        return {
            "note": note,
            "mood": mood,
            "trigger_choice": trigger_choice,
            "trigger_prompt": trigger_question,
            "followup_text": followup_text,
            "followup_q": followup_q,
            "clarity": clarity,
            "clarity_text": clarity_text,
            "clarity_q": clarity_q,
            "close_text": close_text,
            "close_q": close_q,
            "mode": mode,
        }

    def show(self, text):
        self._write(text)

    def show_notice(self, text):
        self._write("  (" + text + ")")

    def rule(self, char):
        self._write(" " + char * IOManager.WIDTH)

    def ledger_line(self, label, value):
        value = str(value)
        if not value:
            value = "-"
        room = IOManager.WIDTH - len(label) - 5
        if len(value) > room:
            value = value[:room - 1] + "…"
        dots = "." * (IOManager.WIDTH - len(label) - len(value) - 2)
        self._write(" " + label + " " + dots + " " + value)

    def print_wrapped(self, text):
        for line in IOManager.wrap_text(text, IOManager.WIDTH - 1):
            self._write(" " + line)

    def show_entry(self, record):
        analysis = record.analysis
        self._write("")
        self._write(" MIRA · " + IOManager.format_stamp(record.timestamp))
        self.rule("─")
        self.ledger_line("Mood", str(record.mood) + " / 5")
        self.ledger_line("Driver", record.trigger_label.split(" — ")[0])
        self.ledger_line("Clarity", record.clarity_label.split(" — ")[0])
        if analysis.emotions:
            self.ledger_line("Feeling", ", ".join(analysis.emotions))
        if analysis.themes:
            self.ledger_line("About", ", ".join(analysis.themes))
        if analysis.congruence:
            self.ledger_line("Words vs rating", analysis.congruence)
        self.rule("─")
        if analysis.reflection:
            self._write(" READING")
            self.print_wrapped(analysis.reflection)
            if analysis.congruence == "diverged" and analysis.congruence_note:
                self._write("")
                self.print_wrapped(analysis.congruence_note)
            if analysis.reframe:
                self._write("")
                self.print_wrapped("❝ " + analysis.reframe + " ❞")
        outcome = self._bank.outcome_label(record.outcome)
        left = "OUTCOME " + outcome
        right = "SCORE " + str(record.score) + "/5"
        gap = IOManager.WIDTH - len(left) - len(right)
        if gap < 2:
            gap = 2
        self.rule("═")
        self._write(" " + left + " " * gap + right)
        self._write("")
        