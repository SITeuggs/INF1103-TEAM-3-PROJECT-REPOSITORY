class Summary:
    def __init__(self, label, count, analysed_count, average, low, high,
                 trajectory, outcome_counts, top_themes, top_emotions,
                 top_triggers):
        self._label = label
        self._count = count
        self._analysed_count = analysed_count
        self._average = average
        self._low = low
        self._high = high
        self._trajectory = trajectory
        self._outcome_counts = dict(outcome_counts)
        self._top_themes = list(top_themes)
        self._top_emotions = list(top_emotions)
        self._top_triggers = list(top_triggers)

    @property
    def label(self):
        return self._label

    @property
    def count(self):
        return self._count

    @property
    def analysed_count(self):
        return self._analysed_count

    @property
    def average(self):
        return self._average

    @property
    def low(self):
        return self._low

    @property
    def high(self):
        return self._high

    @property
    def trajectory(self):
        return self._trajectory

    @property
    def outcome_counts(self):
        return dict(self._outcome_counts)

    @property
    def top_themes(self):
        return list(self._top_themes)

    @property
    def top_emotions(self):
        return list(self._top_emotions)

    @property
    def top_triggers(self):
        return list(self._top_triggers)