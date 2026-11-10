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