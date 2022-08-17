#!/usr/bin/env python3

import asyncio
import logging

import kv_store
import rest
import tcp

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

KV_STORE = kv_store.KVStore()


async def main():
    rest_app = rest.make_tornado_app(kv_store=KV_STORE)
    rest_app.listen(8080)
    tcp_server = tcp.TCPServer(kv_store=KV_STORE)
    tcp_server.listen(8081)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
