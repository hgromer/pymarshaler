import json
import unittest

from pymarshall import marshall
from pymarshall.arg_delegates import ArgBuilderFactory
from tests.test_classes import *


class TestMarshalling(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_simple_marshalling(self):
        inner = Inner("Inner", 10)
        inner_result = _marshall_and_unmarshall(Inner, inner)
        self.assertEqual(inner, inner_result)

    def test_nested_marshalling(self):
        inner = Inner("Inner", 10)
        inner_list = [Inner(f'Inner_{i}', i) for i in range(10)]
        outter = Outter(inner, inner_list)
        outter_result = _marshall_and_unmarshall(Outter, outter)
        self.assertEqual(outter, outter_result)

    def test_multi_nested(self):
        inner = Inner("Inner", 10)
        inner_list = [Inner(f'Inner_{i}', i) for i in range(100)]
        outter = Outter(inner, inner_list)
        multi_nested_outter = MultiNestedOutter(outter)
        result = _marshall_and_unmarshall(MultiNestedOutter, multi_nested_outter)
        self.assertEqual(result, multi_nested_outter)

    def test_multi_nested_list(self):
        nested_list = MultiNestedList(
            [MultiNestedOutter(
                Outter(
                    Inner('Inner', x), [Inner('Inner', 1000)]
                )
            ) for x in range(10)]
        )
        result = _marshall_and_unmarshall(MultiNestedList, nested_list)
        self.assertEqual(result, nested_list)

    def test_datetime_marshalling(self):
        class_with_date = ClassWithDate(datetime.datetime.now())
        result = _marshall_and_unmarshall(ClassWithDate, class_with_date)
        self.assertEqual(class_with_date, result)

    def test_dict_marshalling(self):
        class_with_dict = ClassWithDict({'Test': Inner('inner', 1)})
        result = _marshall_and_unmarshall(ClassWithDict, class_with_dict)
        self.assertEqual(result, class_with_dict)

    def test_fails_on_missing(self):
        self.assertRaises(ValueError, lambda: marshall.unmarshall(Inner, {'name': 'Inner'}))

    def test_ignores_unused(self):
        inner = Inner("Inner", 10)
        marshalled = marshall.marshall(inner)
        j = json.loads(marshalled)
        j['unused'] = 10
        result = marshall.unmarshall(Inner, j)
        self.assertEqual(result, inner)

    def test_default_values(self):
        class_with_defaults = ClassWithDefaults()
        result = marshall.unmarshall(ClassWithDefaults, {})
        self.assertEqual(result, class_with_defaults)

    def test_validate(self):
        self.assertRaises(ValidateError, lambda: marshall.unmarshall(ClassWithValidate, {}))

    def test_custom_delegate(self):
        ArgBuilderFactory.register_delegate(ClassWithCustomDelegate, CustomNoneDelegate)
        result = marshall.unmarshall(ClassWithCustomDelegate, {})
        self.assertEqual(result, ClassWithCustomDelegate())

    def test_nested_lists(self):
        nested_lists = NestedList([[Inner("Inner_1", 1)], [Inner("Inner_2", 2)]])
        result = _marshall_and_unmarshall(NestedList, nested_lists)
        self.assertEqual(nested_lists, result)

    def test_nested_dict_list(self):
        nested = NestedDictList(
            {
                "Test1": {
                    "Test2": NestedList([[Inner("test", 1)], [Inner("test", 2)]])
                }
            }
        )
        result = _marshall_and_unmarshall(NestedDictList, nested)
        self.assertEqual(nested, result)


def _marshall_and_unmarshall(cls, obj):
    marshalled = marshall.marshall(obj)
    return marshall.unmarshall_str(cls, marshalled)


if __name__ == '__main__':
    unittest.main()
