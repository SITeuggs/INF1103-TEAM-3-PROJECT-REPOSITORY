import content

class QuestionBank:
    def mood_band(self, mood):
        if mood >= 4:
            return "high"
        if mood <= 2:
            return "low"
        return "neutral"

    def mood_scale(self):
        return content.MOOD_SCALE

    def mood_text(self, mood):
        if mood in content.MOOD_SCALE.keys():
            return content.MOOD_SCALE[mood]["text"]
        return ""

    def mood_emoji(self, mood):
        if mood in content.MOOD_SCALE.keys():
            return content.MOOD_SCALE[mood]["emoji"]
        return ""

    def trigger_prompt(self, mood):
        return content.TRIGGERS[self.mood_band(mood)]["prompt"]

    def trigger_options(self, mood):
        return content.TRIGGERS[self.mood_band(mood)]["options"]

    def followup_question(self, mood, trigger_choice):
        return content.FOLLOWUPS[self.mood_band(mood)][trigger_choice]

    def clarity_options(self):
        return content.CLARITY_OPTIONS

    def clarity_question(self, clarity, mood):
        return content.CLARITY_FOLLOWUPS[clarity][self.mood_band(mood)]

    def close_prompt(self, mood):
        return content.CLOSE_PROMPTS[self.mood_band(mood)]

    def modes(self):
        return content.MODES

    def outcome_label(self, outcome):
        if outcome in content.OUTCOME_LABELS.keys():
            return content.OUTCOME_LABELS[outcome]
        return "pending"

    def support_contacts(self):
        return content.SUPPORT_CONTACTS

    def labels_for(self, entry):
        mood = entry.mood
        return {
            "mood_label": self.mood_text(mood),
            "trigger_label": self.trigger_options(mood)[entry.trigger_choice],
            "clarity_label": content.CLARITY_OPTIONS[entry.clarity],
            "mode_label": content.MODES[entry.mode],
        }
