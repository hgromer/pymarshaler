import inspect
import typing
from dataclasses import dataclass

from tests.test_classes import Inner


@dataclass
class Test:
    x: str


if __name__ == '__main__':
    print(typing.get_type_hints(Inner))
    print(inspect.signature(Inner.__init__).parameters['name'].annotation)
