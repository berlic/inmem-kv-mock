## About
A mock of in-memory key-value storage service.

## Features
- HTTP REST interface
- Telnet-like interface
- TTL support for elements (lazy eviction)
- Data input and output use JSON serialization

## Supported commands
- `KEYS` — list all keys
- `GET` — retrieve element by key
- `SET` — add/update element by key (with optional TTL)
- `DEL` — remove element by key

## Interfaces

### HTTP
|Command|HTTP Verb|Endpoint|Data|Response|
|-|-|-|-|-|
|`KEYS`|`GET`|`/keys/`||`200`|
|`GET`|`GET`|`/keys/<key>`||`200`,`404`|
|`SET`|`POST`|`/keys/<key>`|`value=<JSON-encoded-value>`<br>`ttl=<ttl-as-float>`|`200`,`400`|
|`DEL`|`DELETE`|`/keys/<key>`||`200`|

### TEXT
|Command|Syntax|Example|
|-|-|-|
|`KEYS`|`KEYS`|`KEYS`|
|`GET`|`GET <key>`|`GET test_item`<br>`GET "foo bar"`|
|`SET`|`SET <key> <JSON-encoded-value> [EX <ttl-as-float>]`|`SET test 1`<br>`SET "foo bar" "{\"k\":[1,2]}" EX 10.5`|
|`DEL`|`DEL <key>`|`DEL test_item`|

Keys and values are expected to be quoted in BASH-like syntax.

## Examples

```
> docker-compose up --build
> nc 127.0.0.1 8081
SET my_key 123
OK
SET "another key" "{\"complex value\":[1,2,3]}" EX 600
OK
KEYS
["my_key", "another key"]
GET "another key"
{"complex value": [1, 2, 3]}
DEL my_key
OK
KEYS
["another key"]
GET my_key
ERR: not found
SET my_key my_val EX abc
ERR: wrong TTL (abc)
^C
```

```
> docker-compose up --build
> curl -X POST -d 'value="bar"' 'localhost:8080/keys/foo'
OK
> curl -X POST -d 'value={"complex value":[1,2,3]}&ttl=600' 'localhost:8080/keys/another%20key'
OK
> curl 'localhost:8080/keys/'
[
  "foo",
  "another key"
]
> curl 'localhost:8080/keys/another%20key'
{
  "complex value": [
    1,
    2,
    3
  ]
}
> curl -X DELETE 'localhost:8080/keys/another%20key'
OK
> curl -i 'localhost:8080/keys/another%20key'
HTTP/1.1 404 Not Found
```

## Tests

To run styling checks, unit tests and get code coverage report use `./check.sh`

```
> ./check.sh
Styling checks:
OK!

Unit tests:
test_delete (test_kv_store.TestCRUD) ... ok
test_delete_missing (test_kv_store.TestCRUD) ... ok
test_set_get (test_kv_store.TestCRUD) ... ok
test_get_ttl (test_kv_store.TestTTL) ... ok
test_keys_ttl (test_kv_store.TestTTL) ... ok
test_delete (test_rest.TestREST) ... ok
test_get_200 (test_rest.TestREST) ... ok
test_get_404 (test_rest.TestREST) ... ok
test_keys (test_rest.TestREST) ... ok
test_set_200 (test_rest.TestREST) ... ok
test_set_400 (test_rest.TestREST) ... ok
test_set_ttl_200 (test_rest.TestREST) ... ok
test_set_ttl_400 (test_rest.TestREST) ... ok

----------------------------------------------------------------------
Ran 13 tests in 5.145s

OK

Code coverage:
Name          Stmts   Miss  Cover   Missing
-------------------------------------------
kv_store.py      35      0   100%
main.py          16     16     0%   3-25
rest.py          38      1    97%   39
tcp.py           63     63     0%   1-81
-------------------------------------------
TOTAL           152     80    47%
```
