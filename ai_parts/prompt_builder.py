class PromptBuilder:
    def __init__(self, question_bank):
        self._bank = question_bank

    def entry_payload(self, entry):
        mood = entry.mood
        mood_desc = self._bank.mood_text(mood)
        trigger_label = self._bank.trigger_options(mood)[entry.trigger_choice]
        clarity_label = self._bank.clarity_options()[entry.clarity]
        mode_label = self._bank.modes()[entry.mode]
        followup = entry.followup_text
        if not followup:
            followup = "Skipped"
        lines = [
            "ENTRY PAYLOAD",
            'Q1 — Note: "' + entry.note + '"',
            "Q2 — Mood: " + str(mood) + '/5 ("' + mood_desc + '")',
            "Q3a — Trigger: " + entry.trigger_choice + " (" + trigger_label + ")",
            'Q3b — Follow-up: "' + followup + '"',
            "Q4 — Clarity: " + entry.clarity + " (" + clarity_label + ")",
            'Q4a — Q: "' + entry.clarity_q + '" A: "' + entry.clarity_text + '"',
            'Q5 — Q: "' + entry.close_q + '" A: "' + entry.close_text + '"',
            "Q6 — Mode: " + entry.mode + " (" + mode_label + ")",
        ]
        return "\n".join(lines)

    def _or_na(self, value):
        if not value:
            return "n/a"
        return str(value)

    def _list_or_na(self, items):
        if not items:
            return "n/a"
        return ", ".join(items)

    def weekly_payload(self, records, trajectory):
        if not records:
            return None
        blocks = []
        number = 1
        for r in records:
            entry = r.entry
            analysis = r.analysis
            lines = [
                "Entry " + str(number) + " (" + r.date + "): mood=" + str(r.mood)
                + "/5 | score=" + self._or_na(r.score)
                + " | sentiment=" + self._or_na(analysis.sentiment)
                + " | congruence=" + self._or_na(analysis.congruence),
                '  note: "' + entry.note[:200] + '"',
                "  trigger: " + self._or_na(r.trigger_label)
                + ' -> "' + entry.followup_text[:150] + '"',
                '  clarity answer: "' + entry.clarity_text[:150] + '"',
                "  emotions: " + self._list_or_na(analysis.emotions),
                "  themes: " + self._list_or_na(analysis.themes),
                '  what they chose to do next: "' + entry.close_text + '"',
            ]
            blocks.append("\n".join(lines))
            number = number + 1
        header = ("WEEKLY BATCH — " + str(len(records)) + " entries\n"
                  + "MOOD TRAJECTORY (already calculated): " + trajectory + "\n"
                  + "========================================\n\n")
        return header + "\n\n".join(blocks)
