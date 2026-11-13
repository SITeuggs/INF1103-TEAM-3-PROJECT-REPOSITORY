import json
import os
from errors.storage_error import StorageError

class ConfigStore:
    def __init__(self, path):
        self._path = path

    def load(self):
        if not os.path.exists(self._path):
            return {}
        try:
            with open(self._path, "r") as f:
                config = json.load(f)
        except (ValueError, OSError):
            return {}
        if not isinstance(config, dict):
            return {}
        return config

    def save(self, config):
        try:
            folder = os.path.dirname(self._path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self._path, "w") as f:
                json.dump(config, f, indent=2)
        except OSError as error:
            raise StorageError("Failed to save config: " + str(error))
