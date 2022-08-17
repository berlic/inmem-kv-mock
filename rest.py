import json

import tornado.web


class GenericHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.kv_store = self.application.settings.get('kv_store')

    def throw_400(self, msg):
        self.set_status(400)
        self.write(f"ERROR: {msg}\n")

    def write_json(self, obj):
        self.write(f"{json.dumps(obj, indent=2)}\n")


class KeysHandler(GenericHandler):
    def get(self):
        self.write_json(self.kv_store.keys())


class KeyHandler(GenericHandler):
    def get(self, path):
        if (item := self.kv_store.get(path)) is not None:
            self.write_json(self.kv_store.get(path))
        else:
            self.set_status(404)

    def post(self, path):
        ttl = self.get_body_argument('ttl', 0)
        try:
            ttl = float(ttl)
        except ValueError as err:
            self.throw_400(f"'ttl' parameter must be float: {err}")
        else:
            value = self.get_body_argument('value', None)
            if value is None:
                self.throw_400("'value' parameter is mandatory")
            else:
                try:
                    item_value = json.loads(value)
                except json.JSONDecodeError as err:
                    self.throw_400(f"JSON decoding error: {err}")
                else:
                    self.kv_store.set(path, item_value, ttl)
                    self.write("OK\n")

    def delete(self, path):
        self.kv_store.delete(path)
        self.write("OK\n")


def make_tornado_app(kv_store):
    return tornado.web.Application(
        [
            (r"/keys/", KeysHandler),
            (r"/keys/(.*)", KeyHandler),
        ],
        kv_store=kv_store
    )
