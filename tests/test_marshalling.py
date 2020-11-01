import json
import unittest

from pymarshall import marshall
from tests.test_classes import *


class TestMarshalling(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_simple_marshalling(self):
        inner = Inner("Inner", 10)
        inner_result = _marshall_and_unmarshall(Inner, inner)
        self.assertTrue(inner == inner_result)

    def test_nested_marshalling(self):
        inner = Inner("Inner", 10)
        inner_list = [Inner(f'Inner_{i}', i) for i in range(10)]
        outter = Outter(inner, inner_list)
        outter_result = _marshall_and_unmarshall(Outter, outter)
        self.assertTrue(outter == outter_result)

    def test_multi_nested(self):
        inner = Inner("Inner", 10)
        inner_list = [Inner(f'Inner_{i}', i) for i in range(100)]
        outter = Outter(inner, inner_list)
        multi_nested_outter = MultiNestedOutter(outter)
        result = _marshall_and_unmarshall(MultiNestedOutter, multi_nested_outter)
        self.assertTrue(result == multi_nested_outter)

    def test_datetime_marshalling(self):
        class_with_date = ClassWithDate(datetime.datetime.now())
        result = _marshall_and_unmarshall(ClassWithDate, class_with_date)
        self.assertTrue(class_with_date == result)

    def test_dict_marshalling(self):
        class_with_dict = ClassWithDict({"Test": 1})
        result = _marshall_and_unmarshall(ClassWithDict, class_with_dict)
        self.assertTrue(result == class_with_dict)

    def test_user_defined_dict_marshalling(self):
        class_with_user_defined_dict = ClassWithUserDefinedDict({"Test": Inner("Inner", 1)})
        result = _marshall_and_unmarshall(ClassWithUserDefinedDict, class_with_user_defined_dict)
        self.assertTrue(result == class_with_user_defined_dict)

    def test_fails_on_missing(self):
        self.assertRaises(ValueError, lambda: marshall.unmarshall(Inner, {'name': 'Inner'}))

    def test_ignores_unused(self):
        inner = Inner("Inner", 10)
        marshalled = marshall.marshall(inner)
        j = json.loads(marshalled)
        j['unused'] = 10
        result = marshall.unmarshall(Inner, j, True)
        self.assertTrue(result == inner)

    def test_default_values(self):
        class_with_defaults = ClassWithDefaults()
        result = marshall.unmarshall(ClassWithDefaults, {})
        self.assertTrue(result == class_with_defaults)

    def test_validate(self):
        self.assertRaises(ValidateError, lambda: marshall.unmarshall(ClassWithValidate, {}))


def _marshall_and_unmarshall(cls, obj):
    marshalled = marshall.marshall(obj)
    return marshall.unmarshall_str(cls, marshalled)


if __name__ == '__main__':
    unittest.main()
