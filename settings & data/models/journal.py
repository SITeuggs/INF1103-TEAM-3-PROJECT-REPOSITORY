class Journal:
    def __init__(self, records=None):
        self._records = []
        if records is not None:
            for r in records:
                self._records.append(r)
        self._sort()

    def _sort(self):
        for i in range(1, len(self._records)):
            for j in range(i, 0, -1):
                if self._records[j].timestamp < self._records[j - 1].timestamp:
                    saved = self._records[j]
                    self._records[j] = self._records[j - 1]
                    self._records[j - 1] = saved
                else:
                    break

    @property
    def records(self):
        return list(self._records)

    def count(self):
        return len(self._records)

    def add(self, record):
        self._records.append(record)

    def find(self, entry_id):
        for r in self._records:
            if r.id == entry_id:
                return r
        return None

    def remove(self, entry_id):
        for i in range(len(self._records)):
            if self._records[i].id == entry_id:
                del self._records[i]
                return True
        return False

    def replace(self, record):
        for i in range(len(self._records)):
            if self._records[i].id == record.id:
                self._records[i] = record
                return True
        return False

    def before(self, timestamp):
        older = []
        for r in self._records:
            if r.timestamp < timestamp:
                older.append(r)
        return Journal(older)

    def analysed(self):
        kept = []
        for r in self._records:
            if r.analysis.was_analysed():
                kept.append(r)
        return kept

    def recent_analysed(self, limit):
        kept = self.analysed()
        if limit <= 0:
            return []
        return kept[-limit:]

    def filter(self, record_filter):
        kept = []
        for r in self._records:
            if record_filter.matches(r):
                kept.append(r)
        return kept
 