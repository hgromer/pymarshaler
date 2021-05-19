from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

from pymarshaler.arg_delegates import ArgBuilderDelegate


@dataclass
class Inner:

    name: str
    value: int


@dataclass
class Outter:

    inner: Inner
    inner_list: List[Inner]


@dataclass
class MultiNestedOutter:

    outter: Outter


@dataclass
class MultiNestedList:

    outter_list: List[MultiNestedOutter]


@dataclass
class ClassWithDate:

    date: datetime.datetime


@dataclass
class ClassWithDefaults:

    value: int = 10


@dataclass
class ClassWithDict:

    d: Dict[str, Inner]


@dataclass
class ClassWithNestedDict:

    d: Dict[str, ClassWithDict]


class ValidateError(Exception):

    def __init__(self):
        super()


@dataclass
class ClassWithValidate:

    def validate(self):
        raise ValidateError()


@dataclass
class ClassWithCustomDelegate:

    pass


@dataclass
class CustomNoneDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data):
        return ClassWithCustomDelegate()


@dataclass
class NestedList:

    multiple_inner_list: List[List[Inner]]


@dataclass
class NestedDictList:

    d: Dict[str, Dict[str, NestedList]]


class EnumClass(Enum):
    VAL = 0
