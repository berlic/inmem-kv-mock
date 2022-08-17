import json
import logging
import shlex

import tornado.tcpserver
from tornado.iostream import StreamClosedError

logger = logging.getLogger(__name__)


def json_bytes(data):
    return (json.dumps(data) + "\n").encode("utf-8")


class TCPServer(tornado.tcpserver.TCPServer):
    def __init__(self, *args, kv_store, **kwargs):
        super(TCPServer, self).__init__(*args, **kwargs)
        self.kv_store = kv_store

    async def handle_stream(self, stream, address):
        async def respond(msg):
            await stream.write((msg+"\n").encode("utf-8"))

        logger.info(f"New TCP connection from {address[0]}:{address[1]}")
        while True:
            try:
                bytes = await stream.read_until(b"\n")
                data = bytes.decode("utf-8").strip()
                logger.info(f"Data from '{address[0]}:{address[1]}' > {data}")
                cmd, *args = shlex.split(data)
                cmd = cmd.upper()
                if len(args) > 0:
                    key = args[0]
                    args = args[1:]
                else:
                    key = None
                if cmd == "KEYS":
                    await stream.write(json_bytes(self.kv_store.keys()))
                elif cmd == "SET":
                    if key is not None:
                        if len(args) not in [1, 3]:
                            await respond("ERR: wrong number of arguments, "
                                          "call 'SET <KEY> <VALUE> [EX <TTL>]")
                            continue
                        elif len(args) == 3 and args[-2] == "EX":
                            try:
                                ttl = float(args[-1])
                            except ValueError as err:
                                await respond(f"ERR: wrong TTL ({args[-1]})")
                                continue
                        else:
                            ttl = 0
                        try:
                            item_value = json.loads(args[0])
                        except json.JSONDecodeError as err:
                            await respond(f"ERR: JSON decoding error: {err}")
                            continue
                        else:
                            self.kv_store.set(key, item_value, ttl)
                            await stream.write(b"OK\n")
                    else:
                        await stream.write(b"ERR: 'key' argument is missing\n")
                elif cmd == "GET":
                    if key is not None:
                        value = self.kv_store.get(key)
                        if value is not None:
                            await stream.write(json_bytes(value))
                        else:
                            await stream.write(b"ERR: not found\n")
                    else:
                        await stream.write(b"ERR: 'key' argument is missing\n")
                elif cmd == "DEL":
                    if key is not None:
                        self.kv_store.delete(key)
                        await stream.write(b"OK\n")
                    else:
                        await stream.write(b"ERR: 'key' argument is missing\n")
                else:
                    await respond("ERR: unsupported command")
            except StreamClosedError as e:
                break
