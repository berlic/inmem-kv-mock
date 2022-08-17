import unittest
from time import sleep

import kv_store


class TestCRUD(unittest.TestCase):
    test_key = "key"
    test_value = "value"

    def test_set_get(self):
        store = kv_store.KVStore()
        self.assertIsNone(store.get(self.test_key))
        store.set(self.test_key, self.test_value)
        self.assertEqual(store.get(self.test_key), self.test_value)

    def test_delete(self):
        store = kv_store.KVStore()
        store.set(self.test_key, self.test_value)
        self.assertIsNotNone(store.get(self.test_key))
        store.delete(self.test_key)
        self.assertIsNone(store.get(self.test_key))

    def test_delete_missing(self):
        store = kv_store.KVStore()
        self.assertIsNone(store.get(self.test_key))
        store.delete(self.test_key)
        self.assertIsNone(store.get(self.test_key))


class TestTTL(unittest.TestCase):
    test_key = "key"
    test_key2 = "key2"
    test_value = "value"
    ttl = 2

    def test_get_ttl(self):
        store = kv_store.KVStore()
        store.set(self.test_key, self.test_value, self.ttl)
        sleep(self.ttl - 0.5)
        self.assertIsNotNone(store.get(self.test_key))
        sleep(1)
        self.assertIsNone(store.get(self.test_key))

    def test_keys_ttl(self):
        store = kv_store.KVStore()
        store.set(self.test_key, self.test_value)
        store.set(self.test_key2, self.test_value, self.ttl)
        sleep(self.ttl - 0.5)
        expected = [self.test_key, self.test_key2]
        self.assertEqual(set(store.keys()), set(expected))
        sleep(1)
        expected = [self.test_key]
        self.assertEqual(set(store.keys()), set(expected))
