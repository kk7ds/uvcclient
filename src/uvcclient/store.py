import base64
import json
import logging
import os

LOG = logging.getLogger(__name__)
_INFO_STORE = None


class UnableToManageStore(Exception):
    pass


class InfoStore:
    def __init__(self, path=None):
        if path is None:
            path = os.path.expanduser(os.path.join("~", ".uvcclient"))
        self._path = path
        self.load()

    def load(self):
        try:
            with open(self._path) as f:
                self._data = json.loads(base64.b64decode(f.read()).decode())
        except OSError:
            LOG.debug("No info store")
            self._data = {}
        except Exception as ex:
            LOG.error("Failed to read store data: %s", ex)
            raise UnableToManageStore("Unable to write to store") from ex

    def save(self):
        try:
            with open(self._path, "w") as f:
                f.write(base64.b64encode(json.dumps(self._data).encode()).decode())
            os.chmod(self._path, 0o600)
        except OSError as ex:
            LOG.error("Unable to write store: %s", str(ex))
            raise UnableToManageStore("Unable to write to store") from ex

    def get_camera_passwords(self):
        return self._data.get("camera_passwords", {})

    def get_camera_password(self, uuid):
        return self.get_camera_passwords().get(uuid)

    def set_camera_password(self, uuid, password):
        if "camera_passwords" not in self._data:
            self._data["camera_passwords"] = {}
        self._data["camera_passwords"][uuid] = password
        self.save()


def get_info_store(path=None):
    global _INFO_STORE
    if _INFO_STORE is None:
        _INFO_STORE = InfoStore(path)
    return _INFO_STORE
