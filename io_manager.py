from io_parts.choice_validator import ChoiceValidator
from io_parts.date_validator import DateValidator
from io_parts.non_empty_validator import NonEmptyValidator
from models.record_filter import RecordFilter
from settings import Settings

class IOManager:
    WIDTH = 58
    MENU_CHOICES = ("1", "2", "3", "4", "5", "6", "7", "q")
    MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    OUTCOME_ORDER = ("accept", "check_in", "flag")
    
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
        self._write("  [4] Get support     [5] Filter data     [6] Edit an entry")
        self._write("  [7] Delete an entry [q] Quit")
        choice = self.ask("", ChoiceValidator(
            IOManager.MENU_CHOICES, "Pick 1, 2, 3, 4, 5, 6, 7, or q."))
        return choice.lower()

    def ask_name(self):
        name = self._read("\n  Welcome to MIRA! What's your name?  > ").strip()
        return name

    def ask_entry_id(self, action):
        return self.ask("Entry id to " + action,
                        NonEmptyValidator("Type the id from the entry list."))

    def ask_confirm(self, question):
        answer = self.ask(question + " (y/n)",
                          ChoiceValidator(("y", "n"), "Enter y or n."))
        return answer.lower() == "y"

    def ask_filter(self):
        self._write("\n  Narrow down your entries. Press Enter to skip any question.")
        self._write("\n  Which kind of entries?")
        for number in range(len(IOManager.OUTCOME_ORDER)):
            self._write("    " + str(number + 1) + "  "
                        + self._bank.outcome_label(IOManager.OUTCOME_ORDER[number]))
        pick = self.ask("Pick 1, 2 or 3 (Enter for all)",
                        ChoiceValidator(("1", "2", "3"), "Enter 1, 2 or 3, or press Enter.",
                                        allow_blank=True))
        self._write("")
        mood_error = "Enter a number from 1 to 5, or press Enter."
        low = self.ask("Lowest mood to include, 1 = struggling",
                       ChoiceValidator("12345", mood_error, allow_blank=True))
        high = self.ask("Highest mood to include, 5 = really good",
                        ChoiceValidator("12345", mood_error, allow_blank=True))
        since = self.ask("Only entries from this date, like 2026-10-23",
                         DateValidator(allow_blank=True))
        until = self.ask("Only entries up to this date, like 2026-10-30",
                         DateValidator(allow_blank=True))
        keyword = self.ask("A topic or word to look for, like exams",
                           NonEmptyValidator(allow_blank=True))
        outcome = None
        if pick:
            outcome = IOManager.OUTCOME_ORDER[int(pick) - 1]
        if low and high and int(low) > int(high):
            low, high = high, low
            self._write("  (Lowest and highest were the wrong way round, so I swapped them.)")
        if since and until and since > until:
            since, until = until, since
            self._write("  (The dates were the wrong way round, so I swapped them.)")
        return RecordFilter(
            outcome,
            int(low) if low else None,
            int(high) if high else None,
            since if since else None,
            until if until else None,
            keyword if keyword else None,
        )

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

    def show_entries(self, records, empty_message="No entries yet."):
        if not records:
            self._write("\n  " + empty_message + "\n")
            return
        pad_right = IOManager.pad_right
        pad_left = IOManager.pad_left
        limit = self._settings.HISTORY_LIMIT
        self._write("")
        self._write("  " + pad_right("ID", 10) + " " + pad_right("Date", 12) + " "
                    + pad_left("Mood", 4) + "  " + pad_right("Trigger", 26) + " "
                    + pad_right("Outcome", 19))
        self._write("  " + "─" * 10 + " " + "─" * 12 + " "
                    + "─" * 4 + "  " + "─" * 26 + " " + "─" * 19)
        for r in records[-limit:]:
            mood = r.mood
            if not mood:
                mood = 3
            emoji = self._bank.mood_emoji(mood)
            outcome = r.outcome
            if outcome:
                outcome = self._bank.outcome_label(outcome)
            else:
                outcome = "pending"
            self._write("  " + pad_right(r.id, 10) + " " + pad_right(r.date, 12)
                        + " " + pad_left(emoji, 4) + "  "
                        + pad_right(r.trigger_label[:26], 26) + " "
                        + pad_right(outcome, 19))
        shown = len(records)
        if shown > limit:
            shown = limit
        self._write("\n  Showing " + str(shown) + " of " + str(len(records))
                    + " entries.\n")

    def show_weekly(self, result, count, trajectory):
        self._write("")
        self._write(" MIRA · WEEKLY REVIEW · " + str(count) + " ENTRIES")
        self.rule("─")
        self.ledger_line("Mood trajectory", trajectory)
        self.rule("─")
        self._write(" PATTERN")
        self.print_wrapped(result["dominant_pattern"])
        self._write("")
        self._write(" YOUR BEST MOVE")
        self.print_wrapped(result["best_mechanism"])
        self._write("")
        self._write(" FRICTION POINT")
        self.print_wrapped(result["friction_point"])
        self._write("")
        self.rule("─")
        self._write(" REFLECTION")
        self.print_wrapped(result["summary"])
        self._write("")
        self._write(" CARRY INTO NEXT WEEK")
        self.print_wrapped(result["carry_forward"])
        self.rule("═")
        self._write("")

    def show_weekly_snapshot(self, count, trajectory, low, high, mean):
        self._write("")
        self._write(" MIRA · WEEKLY SNAPSHOT · " + str(count) + " ENTRIES")
        self.rule("─")
        if count > 0:
            self.ledger_line("Mood trajectory", trajectory)
            self.ledger_line("Range", str(low) + " to " + str(high))
            self.ledger_line("Average", str(round(mean, 1)))
            self.rule("─")
        short_by = self._settings.MIN_ENTRIES_FOR_REVIEW - count
        if short_by == 1:
            self.print_wrapped("One more entry and MIRA can look for "
                               "patterns across your entries.")
        else:
            self.print_wrapped(str(short_by) + " more entries and MIRA can look "
                               "for patterns across your entries.")
        self.rule("═")
        self._write("")

    def show_support(self, contacts):
        self._write("")
        self.rule("═")
        self._write(" GET SUPPORT")
        self._write(" If today feels heavy, these services can help.")
        self.rule("─")
        for item in contacts:
            self.ledger_line(item["name"], item["contact"])
        self.rule("═")
        self._write("")

    def _entries_phrase(self, number):
        if number == 1:
            return "1 entry"
        return str(number) + " entries"

    def _words_with_counts(self, pairs):
        text = ""
        for pair in pairs:
            if text:
                text = text + ", "
            text = text + pair[0] + " (" + self._entries_phrase(pair[1]) + ")"
        if not text:
            return "none found"
        return text

    def show_filter_summary(self, summary):
        directions = {
            "rising": "getting better",
            "falling": "getting lower",
            "flat": "staying about the same",
            "volatile": "going up and down a lot",
        }
        self._write("")
        self._write(" ABOUT THESE " + self._entries_phrase(summary.count).upper())
        self.rule("─")
        if summary.low == 0:
            self._write(" Mood: not recorded for these entries.")
        else:
            self._write(" Average mood: " + str(round(summary.average, 1)) + " out of 5")
            self._write("   (1 = struggling, 5 = really good)")
            if summary.low == summary.high:
                self._write(" Every mood rating was " + str(summary.low) + ".")
            else:
                self._write(" Your moods ranged from " + str(summary.low) + " to "
                            + str(summary.high) + ".")
            if summary.count >= 2:
                self._write(" Across these entries, your mood was "
                            + directions[summary.trajectory] + ".")
        self._write("")
        self._write(" How they were marked:")
        counts = summary.outcome_counts
        for outcome in ("accept", "check_in", "flag"):
            self._write("   " + str(counts[outcome]) + "  "
                        + self._bank.outcome_label(outcome))
        self._write("")
        self._write(" What came up most often:")
        self.print_wrapped("Trigger: " + self._words_with_counts(summary.top_triggers[:1]))
        if summary.analysed_count == 0:
            self.print_wrapped("The AI has not read these entries, so there are "
                               "no themes or feelings to show.")
        else:
            self.print_wrapped("Themes: " + self._words_with_counts(summary.top_themes))
            self.print_wrapped("Feelings: " + self._words_with_counts(summary.top_emotions))
            if summary.analysed_count < summary.count:
                self.print_wrapped("(Themes and feelings come from the "
                                   + str(summary.analysed_count)
                                   + " entries the AI read.)")
        self.rule("═")

    def show_comparison(self, current, previous, direction):
        self._write("")
        self._write(" WEEK OVER WEEK")
        self.rule("─")
        self.ledger_line("Entries", str(previous.count) + " -> " + str(current.count))
        if direction == "not enough data":
            self.ledger_line("Average mood", "not enough data")
        else:
            self.ledger_line("Average mood",
                             str(round(previous.average, 1)) + " -> "
                             + str(round(current.average, 1)))
        self.ledger_line("Direction", direction)
        now_counts = current.outcome_counts
        before_counts = previous.outcome_counts
        for outcome in IOManager.OUTCOME_ORDER:
            self.ledger_line(self._bank.outcome_label(outcome),
                             str(before_counts[outcome]) + " -> "
                             + str(now_counts[outcome]))
        self.rule("═")
        self._write("")

    def show_current_note(self, record):
        self._write("")
        self._write(" " + record.date + " · mood " + str(record.mood) + " / 5")
        self.rule("─")
        self.print_wrapped(record.entry.note)
        self.rule("─")