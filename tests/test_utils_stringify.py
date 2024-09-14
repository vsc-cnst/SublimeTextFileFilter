import sys
import unittest

stringify = sys.modules["File Filter.utils.utils"].stringify

class TestStringify(unittest.TestCase):

    def test_none(self):
        self.assertEqual(stringify(None), "None")

    def test_string(self):
        self.assertEqual(stringify("hello"), "'hello'")
        self.assertEqual(stringify("world"), "'world'")

    def test_int_float_bool(self):
        self.assertEqual(stringify(123), "123")
        self.assertEqual(stringify(45.67), "45.67")
        self.assertEqual(stringify(True), "True")
        self.assertEqual(stringify(False), "False")

    def test_list(self):
        self.assertEqual(stringify([1, 2, 3]), "[1, 2, 3]")
        self.assertEqual(stringify(["a", "b", "c"]), "['a', 'b', 'c']")
        self.assertEqual(stringify([None, True, 3.14]), "[None, True, 3.14]")

    def test_tuple(self):
        self.assertEqual(stringify((1, 2, 3)), "[1, 2, 3]")
        self.assertEqual(stringify(("a", "b", "c")), "['a', 'b', 'c']")
        self.assertEqual(stringify((None, False, 2.71)), "[None, False, 2.71]")

    def test_dict(self):
        self.assertEqual(stringify({"a": 1, "b": 2}), "{'a': 1, 'b': 2}")
        self.assertEqual(stringify({1: "x", 2: "y"}), "{1: 'x', 2: 'y'}")
        self.assertEqual(stringify({None: True, "pi": 3.14}), "{None: True, 'pi': 3.14}")

    def test_args_and_kwargs(self):
        self.assertEqual(stringify(1, "test", key="value", another=42), "1, 'test', key: 'value', another: 42")
        self.assertEqual(stringify([1, 2], {"key": "val"}, name="item", price=9.99), "[1, 2], {'key': 'val'}, name: 'item', price: 9.99")

    def test_mixed_objects(self):
        obj = object()
        self.assertEqual(stringify(obj), str(obj))
        self.assertEqual(stringify(obj, name="test"), f"{str(obj)}, name: 'test'")
