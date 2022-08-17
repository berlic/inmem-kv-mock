import json
import logging
from dataclasses import dataclass

from tornado.testing import AsyncHTTPTestCase

import rest

logging.getLogger('tornado.access').disabled = True


class MockedKV(object):
    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def keys(self):
        return list(self.data.keys())

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, value, ttl):
        self.data[key] = {
            "value": value,
            "ttl": ttl,
        }

    def delete(self, key):
        self.data.pop(key, None)


class TestREST(AsyncHTTPTestCase):

    kv_store = MockedKV()

    def get_app(self):
        return rest.make_tornado_app(kv_store=self.kv_store)

    def test_keys(self):
        data = {"one": 1, "two": 2}
        self.kv_store.set_data(data)
        response = self.fetch("/keys/")
        self.assertEqual(response.code, 200)
        self.assertEqual(json.dumps(json.loads(response.body)),
                         json.dumps(list(data.keys())))

    def test_get_200(self):
        key = "one"
        value = 1
        self.kv_store.set_data({key: value})
        response = self.fetch(f"/keys/{key}")
        self.assertEqual(response.code, 200)
        self.assertEqual(json.dumps(json.loads(response.body)),
                         json.dumps(value))

    def test_get_404(self):
        key = "one"
        self.kv_store.set_data({})
        response = self.fetch(f"/keys/{key}")
        self.assertEqual(response.code, 404)

    def test_set_200(self):
        key = "one"
        value = [1, 2, 3]
        response = self.fetch(f"/keys/{key}",
                              method="POST",
                              body=f"value={json.dumps(value)}")
        self.assertEqual(response.code, 200)
        item = self.kv_store.get_data()[key]
        self.assertEqual(item['value'], value)
        self.assertEqual(item['ttl'], 0.0)

    def test_set_400(self):
        key = "one"
        response = self.fetch(f"/keys/{key}", method="POST", body=f"value=_")
        self.assertEqual(response.code, 400)

    def test_set_ttl_200(self):
        key = "one"
        value = [1, 2, 3]
        ttl = 3.5
        response = self.fetch(f"/keys/{key}",
                              method="POST",
                              body=f"value={json.dumps(value)}&ttl={ttl}")
        self.assertEqual(response.code, 200)
        item = self.kv_store.get_data()[key]
        self.assertEqual(item['value'], value)
        self.assertEqual(item['ttl'], ttl)

    def test_set_ttl_400(self):
        key = "one"
        response = self.fetch(f"/keys/{key}",
                              method="POST",
                              body=f"value=0&ttl=_")
        self.assertEqual(response.code, 400)

    def test_delete(self):
        key = "one"
        self.kv_store.set_data({key: 0})
        self.assertIn(key, self.kv_store.get_data().keys())
        response = self.fetch(f"/keys/{key}", method="DELETE")
        self.assertEqual(response.code, 200)
        self.assertNotIn(key, self.kv_store.get_data().keys())
