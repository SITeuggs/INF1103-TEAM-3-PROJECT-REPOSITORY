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

    def load_samples(self, path, today):
        try:
            with open(path, "r", encoding="utf-8") as f:
                rows = json.load(f)
        except OSError:
            raise StorageError("Could not find the sample file: " + str(path))
        except ValueError:
            raise StorageError("The sample file is damaged: " + str(path))
        if not isinstance(rows, list):
            raise StorageError("The sample file is not a list of entries")
        added = 0
        skipped = 0
        for sample in rows:
            if not isinstance(sample, dict):
                skipped = skipped + 1
                continue
            row = dict(sample)
            try:
                days_ago = int(row.pop("days_ago"))
            except (KeyError, ValueError, TypeError):
                skipped = skipped + 1
                continue
            when = today - timedelta(days=days_ago)
            row["timestamp"] = str(when) + "T" + str(row.pop("time", "09:00:00"))
            record = EntryRecord.from_row(row)
            if not record.id or self._journal.find(record.id) is not None:
                skipped = skipped + 1
                continue
            if not self.add_record(record):
                raise StorageError(self._last_error)
            added = added + 1
        return added, skipped

    def update_record(self, record):
        fields = record.to_row()
        del fields["id"]
        found = self._storage.update(record.id, fields)
        if found:
            self._journal.replace(record)
        return found

    def remove_record(self, entry_id):
        found = self._storage.delete(entry_id)
        self._journal.remove(entry_id)
        return found

    def get_profile(self):
        config = self._config.load()
        if "profile" in config.keys():
            return config["profile"]
        return None

    def set_profile(self, name):
        config = self._config.load()
        config["profile"] = name
        self._config.save(config)

    def samples_were_loaded(self):
        config = self._config.load()
        return config.get("samples_loaded", False) is True

    def mark_samples_loaded(self):
        config = self._config.load()
        config["samples_loaded"] = True
        self._config.save(config)
