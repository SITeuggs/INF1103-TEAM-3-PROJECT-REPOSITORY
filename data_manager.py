import json
from datetime import timedelta
from errors.storage_error import StorageError
from models.entry_record import EntryRecord
from models.journal import Journal

class DataManager:
    def __init__(self, storage, config_store):
        self._storage = storage
        self._config = config_store
        self._journal = Journal()
        self._last_error = ""

    @property
    def journal(self):
        return self._journal

    @property
    def last_error(self):
        return self._last_error

    @property
    def storage_name(self):
        return self._storage.describe()

    def load(self):
        rows = self._storage.load_all()
        records = []
        for row in rows:
            records.append(EntryRecord.from_row(row))
        self._journal = Journal(records)
        return self._journal.count()

    def find_record(self, entry_id):
        return self._journal.find(entry_id)

    def query(self, record_filter):
        return self._journal.filter(record_filter)

    def add_record(self, record):
        self._journal.add(record)
        try:
            self._storage.save(record.to_row())
        except StorageError as error:
            self._last_error = str(error)
            return False
        return True
