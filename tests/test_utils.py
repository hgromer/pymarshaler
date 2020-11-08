import unittest

from pymarshaler.utils import is_user_defined, is_builtin
from tests.test_classes import *


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_is_user_defined(self):
        self.assertTrue(is_user_defined(Inner))
        self.assertTrue(is_user_defined(Outter))
        self.assertFalse(is_user_defined(datetime.datetime))
        self.assertFalse(is_user_defined(dict))

    def test_is_builtin(self):
        self.assertTrue(is_builtin(str))
        self.assertTrue(is_builtin(dict))
        self.assertFalse(is_builtin(Inner))
        self.assertFalse(is_builtin(Outter))
        self.assertFalse(is_builtin(datetime.datetime))


if __name__ == '__main__':
    unittest.main()
