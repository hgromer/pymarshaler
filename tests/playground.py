import typing
from dataclasses import dataclass

import orjson.orjson

import pymarshaler


@dataclass
class MoreInner:
    ids: typing.Set[int]

    def __init__(self, ids: typing.Set[int]):
        self.ids = ids


@dataclass
class InnerTest:
    more_inner: MoreInner

    def __init__(self, more_inner: MoreInner):
        self.more_inner = more_inner


@dataclass
class Test:
    inner: InnerTest

    def __init__(self, inner: InnerTest):
        self.inner = inner


if __name__ == '__main__':
    marshal = pymarshaler.Marshal(True, True)

    ids = {i for i in range(100)}
    test = Test(InnerTest(MoreInner(ids)))

    string = marshal.marshal(test)
    print(f"The string is {string}")

    json_loads = orjson.loads(string)
    print(f"json_loads is {json_loads}")

    marshal_loads = marshal.unmarshal_str(Test, string)
    print(f"marshal_loads is {marshal_loads}")