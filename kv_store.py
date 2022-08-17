import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def now():
    return datetime.timestamp(datetime.now())


class KVItem(object):
    def __init__(self, value, ttl=0):
        self.created = now()
        self.value = value
        self.ttl = ttl

    def is_expired(self):
        if self.ttl != 0 and now() > self.created + self.ttl:
            return True
        return False


class KVStore(object):
    def __init__(self):
        self.store = {}

    def keys(self):
        keys = []
        for key in list(self.store.keys()):
            if self.get(key) is not None:
                keys.append(key)
        return keys

    def get(self, key):
        if (item := self.store.get(key, None)) is not None:
            if item.is_expired():
                logger.info(f"Removed stale item: '{key}'.")
                del self.store[key]
                return None
            else:
                return item.value
        return None

    def set(self, key, value, ttl=0):
        self.store[key] = KVItem(value, ttl)

    def delete(self, key):
        self.store.pop(key, None)
