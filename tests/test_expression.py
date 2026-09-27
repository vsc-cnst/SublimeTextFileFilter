import unittest
import sys

Expression = sys.modules["File Filter.utils.expression"].Expression


class TestExpression(unittest.TestCase):

    def setUp(self):
        self.logger = None

    def test_create_from_string(self):
        expr = Expression.new("regex")
        self.assertEqual(expr.pattern, "regex")
        self.assertEqual(expr.type, "and")
        self.assertEqual(expr.name, "")
        self.assertEqual(expr.code, "")
        self.assertEqual(expr.color, "white")
        self.assertFalse(expr.escape)

    def test_create_from_dict_simple(self):
        data = {
            "code": "simple-pattern",
            "name": "Simple Pattern",
            "type": "and",
            "color": "red",
            "pattern": "regex"
        }
        expr = Expression.new(data)
        self.assertEqual(expr.code, "simple-pattern")
        self.assertEqual(expr.name, "Simple Pattern")
        self.assertEqual(expr.type, "and")
        self.assertEqual(expr.color, "red")
        self.assertEqual(expr.pattern, "regex")

    def test_create_from_list(self):
        expr = Expression.new(["regex1", "regex2"])
        self.assertEqual(expr.type, "and")
        self.assertEqual(len(expr.pattern), 2)
        self.assertIsInstance(expr.pattern[0], Expression)
        self.assertEqual(expr.pattern[0].pattern, "regex1")
        self.assertIsInstance(expr.pattern[1], Expression)
        self.assertEqual(expr.pattern[1].pattern, "regex2")

    def test_compile_string_pattern(self):
        expr = Expression.new("regex")
        compiled = expr.compile()
        self.assertEqual(compiled, "(regex)")

    def test_compile_list_pattern_with_and_type(self):
        expr = Expression.new(["regex1", "regex2"])
        compiled = expr.compile()
        self.assertEqual(compiled, "((regex1)(regex2))")

    def test_compile_with_or_type(self):
        expr = Expression.new(["regex1", "regex2"], type="or")
        compiled = expr.compile()
        self.assertEqual(compiled, "((regex1)|(regex2))")

    def test_invalid_type_defaults_to_and(self):
        expr = Expression.new("regex", type="invalid")
        self.assertEqual(expr.type, "and")

    def test_escape_applies_to_string_patterns(self):
        expr = Expression.new("a.b", escape=True)
        self.assertEqual(expr.pattern, r"a\.b")
        self.assertEqual(expr.compile(), r"(a\.b)")

    def test_invalid_data_raises_error(self):
        with self.assertRaises(ValueError):
            Expression.new(12345)

    def test_invalid_pattern_raises_error(self):
        with self.assertRaises(ValueError):
            Expression.new({"pattern": 12345})


if __name__ == "__main__":
    unittest.main()
