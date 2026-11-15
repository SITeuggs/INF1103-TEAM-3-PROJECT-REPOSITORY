from datetime import timedelta
from models.record_filter import RecordFilter
from models.summary import Summary

class HistoryAnalyser:
    OUTCOMES = ("accept", "check_in", "flag")
    TOP_SHOWN = 3

    def __init__(self, settings):
        self._days = settings.COMPARE_DAYS
        self._volatile_swing = settings.VOLATILE_SWING
        self._trend_change = settings.TREND_CHANGE

    def values(self, records):
        moods = []
        for r in records:
            if r.mood:
                moods.append(r.mood)
        return moods

    def mood_range(self, records):
        moods = self.values(records)
        if not moods:
            return 0, 0
        return min(moods), max(moods)

    def average(self, records):
        moods = self.values(records)
        if not moods:
            return 0
        return self._mean(moods)

    def _mean(self, numbers):
        total = 0
        for n in numbers:
            total = total + n
        return total / len(numbers)

    def trajectory(self, records):
        moods = self.values(records)
        if len(moods) < 2:
            return "flat"
        if len(moods) >= 4:
            total_swing = 0
            for i in range(1, len(moods)):
                step = moods[i] - moods[i - 1]
                if step < 0:
                    step = -step
                total_swing = total_swing + step
            if total_swing / (len(moods) - 1) >= self._volatile_swing:
                return "volatile"
        half = len(moods) // 2
        change = self._mean(moods[-half:]) - self._mean(moods[:half])
        if change >= self._trend_change:
            return "rising"
        if change <= -self._trend_change:
            return "falling"
        return "flat"

    def _count_words(self, words, counts):
        for word in words:
            if word:
                if word in counts.keys():
                    counts[word] = counts[word] + 1
                else:
                    counts[word] = 1

    def _most_common(self, counts):
        pairs = []
        for word in counts.keys():
            pairs.append((word, counts[word]))
        for i in range(len(pairs)):
            best = i
            for j in range(i + 1, len(pairs)):
                if pairs[j][1] > pairs[best][1]:
                    best = j
                elif pairs[j][1] == pairs[best][1] and pairs[j][0] < pairs[best][0]:
                    best = j
            saved = pairs[i]
            pairs[i] = pairs[best]
            pairs[best] = saved
        return pairs[:HistoryAnalyser.TOP_SHOWN]

    def summarise(self, records, label=""):
        outcome_counts = {}
        for outcome in HistoryAnalyser.OUTCOMES:
            outcome_counts[outcome] = 0
        themes = {}
        emotions = {}
        triggers = {}
        analysed = 0
        for r in records:
            if r.outcome in outcome_counts.keys():
                outcome_counts[r.outcome] = outcome_counts[r.outcome] + 1
            self._count_words([r.trigger_label], triggers)
            if r.analysis.was_analysed():
                analysed = analysed + 1
                self._count_words(r.analysis.lowered_themes(), themes)
                lowered_emotions = []
                for e in r.analysis.emotions:
                    lowered_emotions.append(e.lower())
                self._count_words(lowered_emotions, emotions)
        low, high = self.mood_range(records)
        return Summary(
            label, len(records), analysed,
            self.average(records), low, high,
            self.trajectory(records),
            outcome_counts,
            self._most_common(themes),
            self._most_common(emotions),
            self._most_common(triggers),
        )

    def direction(self, current, previous):
        if current.count == 0 or previous.count == 0:
            return "not enough data"
        difference = current.average - previous.average
        if difference >= self._trend_change:
            return "up"
        if difference <= -self._trend_change:
            return "down"
        return "steady"

    def compare_weeks(self, journal, today):
        current_start = today - timedelta(days=self._days - 1)
        previous_start = current_start - timedelta(days=self._days)
        previous_end = current_start - timedelta(days=1)
        current = self.summarise(
            journal.filter(RecordFilter(since=str(current_start),
                                        until=str(today))), "This week")
        previous = self.summarise(
            journal.filter(RecordFilter(since=str(previous_start),
                                        until=str(previous_end))),
            "Previous week")
        return current, previous, self.direction(current, previous)
