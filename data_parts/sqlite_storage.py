import os
import sqlite3
from data_parts.record_storage import RecordStorage
from errors.storage_error import StorageError
from models.entry_record import EntryRecord

class SQLiteStorage(RecordStorage):
    def __init__(self, path):
        self._path = path
        self.__connection = None

    def describe(self):
        return "the local database"

    def _connect(self):
        if self.__connection is not None:
            return self.__connection
        connection = None
        try:
            folder = os.path.dirname(self._path)
            if folder and self._path != ":memory:":
                os.makedirs(folder, exist_ok=True)
            connection = sqlite3.connect(self._path)
            columns = ""
            for i in range(len(EntryRecord.FIELDNAMES)):
                if i > 0:
                    columns = columns + ", "
                name = EntryRecord.FIELDNAMES[i]
                if name == "id":
                    columns = columns + "id TEXT PRIMARY KEY"
                else:
                    columns = columns + name + " TEXT"
            connection.execute("CREATE TABLE IF NOT EXISTS entries (" + columns + ")")
            connection.commit()
        except (sqlite3.Error, OSError) as error:
            if connection is not None:
                connection.close()
            raise StorageError("Could not open the database: " + str(error))
        self.__connection = connection
        return connection

    def close(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None

    def load_all(self):
        connection = self._connect()
        names = ", ".join(EntryRecord.FIELDNAMES)
        try:
            cursor = connection.execute(
                "SELECT " + names + " FROM entries ORDER BY timestamp")
            found = cursor.fetchall()
        except sqlite3.Error as error:
            raise StorageError("Could not read the database: " + str(error))
        rows = []
        for values in found:
            row = {}
            for i in range(len(EntryRecord.FIELDNAMES)):
                row[EntryRecord.FIELDNAMES[i]] = values[i]
            rows.append(row)
        return rows

    def save(self, row):
        connection = self._connect()
        names = ""
        marks = ""
        values = []
        for i in range(len(EntryRecord.FIELDNAMES)):
            if i > 0:
                names = names + ", "
                marks = marks + ", "
            names = names + EntryRecord.FIELDNAMES[i]
            marks = marks + "?"
            values.append(str(row.get(EntryRecord.FIELDNAMES[i], "")))
        try:
            connection.execute(
                "INSERT INTO entries (" + names + ") VALUES (" + marks + ")",
                values)
            connection.commit()
        except sqlite3.Error as error:
            raise StorageError("Could not save to the database: " + str(error))

    def update(self, entry_id, fields):
        connection = self._connect()
        assignments = ""
        values = []
        for key in fields.keys():
            if key not in EntryRecord.FIELDNAMES or key == "id":
                raise StorageError("Cannot update the column '" + key + "'")
            if assignments:
                assignments = assignments + ", "
            assignments = assignments + key + " = ?"
            values.append(str(fields[key]))
        if not assignments:
            return False
        values.append(entry_id)
        try:
            cursor = connection.execute(
                "UPDATE entries SET " + assignments + " WHERE id = ?", values)
            connection.commit()
        except sqlite3.Error as error:
            raise StorageError("Could not update the database: " + str(error))
        return cursor.rowcount > 0

    def delete(self, entry_id):
        connection = self._connect()
        try:
            cursor = connection.execute("DELETE FROM entries WHERE id = ?",
                                        (entry_id,))
            connection.commit()
        except sqlite3.Error as error:
            raise StorageError("Could not delete from the database: " + str(error))
        return cursor.rowcount > 0
