import datetime
from typing import List, Dict

from pymarshall.arg_delegates import ArgBuilderDelegate


class EqualityBuiltIn:

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if len(self.__dict__) != len(other.__dict__):
            return False
        for key, value in self.__dict__.items():
            if key not in other.__dict__:
                return False
            elif value != other.__dict__[key]:
                return False
        return True


class Inner(EqualityBuiltIn):

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value


class Outter(EqualityBuiltIn):

    def __init__(self, inner: Inner, inner_list: List[Inner]):
        self.inner = inner
        self.inner_list = inner_list


class MultiNestedOutter(EqualityBuiltIn):

    def __init__(self, outter: Outter):
        self.outter = outter


class MultiNestedList(EqualityBuiltIn):

    def __init__(self, outter_list: List[MultiNestedOutter]):
        self.outter_list = outter_list


class ClassWithDate(EqualityBuiltIn):

    def __init__(self, date: datetime.datetime):
        self.date = date


class ClassWithDefaults(EqualityBuiltIn):

    def __init__(self, value: int = 10):
        self.value = value


class ClassWithDict(EqualityBuiltIn):

    def __init__(self, d: Dict[str, Inner]):
        self.d = d


class ValidateError(Exception):

    def __init__(self):
        super()


class ClassWithValidate:

    def __init__(self):
        pass

    def validate(self):
        raise ValidateError()


class ClassWithCustomDelegate(EqualityBuiltIn):

    def __init__(self):
        pass


class CustomNoneDelegate(ArgBuilderDelegate):

    def resolve(self, data):
        return {}
