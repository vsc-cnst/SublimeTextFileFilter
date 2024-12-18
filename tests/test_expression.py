import unittest
import logging
from expression import Expression  # Replace with the actual file/module name


class TestExpression(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestExpression")
        self.logger.setLevel(logging.DEBUG)

    def test_create_from_string(self):
        expr = Expression.new("regex", logger=self.logger)
        self.assertEqual(expr.pattern, "regex")
        self.assertEqual(expr.type, "and")
        self.assertEqual(expr.name, "")
        self.assertEqual(expr.description, "")

    def test_create_from_dict_simple(self):
        data = {
            "name": "Simple Pattern",
            "description": "A simple regex pattern",
            "type": "and",
            "pattern": "regex"
        }
        expr = Expression.new(data, logger=self.logger)
        self.assertEqual(expr.name, "Simple Pattern")
        self.assertEqual(expr.description, "A simple regex pattern")
        self.assertEqual(expr.type, "and")
        self.assertEqual(expr.pattern, "regex")

    def test_create_from_dict_nested(self):
        data = {
            "name": "Nested Pattern",
            "description": "A nested regex pattern",
            "type": "and",
            "pattern": {
                "name": "Inner Pattern",
                "pattern": "inner_regex"
            }
        }
        expr = Expression.new(data, logger=self.logger)
        self.assertEqual(expr.name, "Nested Pattern")
        self.assertEqual(expr.description, "A nested regex pattern")
        self.assertIsInstance(expr.pattern, Expression)
        self.assertEqual(expr.pattern.name, "Inner Pattern")
        self.assertEqual(expr.pattern.pattern, "inner_regex")

    def test_create_from_list(self):
        data = [
            "regex1",
            {
                "pattern": "regex2"
            },
            {
                "name": "Nested",
                "pattern": ["nested_regex1", "nested_regex2"]
            }
        ]
        expr = Expression.new(data, logger=self.logger)
        self.assertEqual(expr.type, "and")
        self.assertEqual(len(expr.pattern), 3)
        self.assertEqual(expr.pattern[0], "regex1")
        self.assertIsInstance(expr.pattern[1], Expression)
        self.assertEqual(expr.pattern[1].pattern, "regex2")
        self.assertIsInstance(expr.pattern[2], Expression)
        self.assertEqual(expr.pattern[2].pattern[0], "nested_regex1")

    def test_compile_string_pattern(self):
        expr = Expression.new("regex", logger=self.logger)
        compiled = expr.compile()
        self.assertEqual(compiled, "(regex)")

    def test_compile_nested_pattern(self):
        data = {
            "name": "Nested",
            "type": "and",
            "pattern": [
                "regex1",
                {"pattern": "regex2"}
            ]
        }
        expr = Expression.new(data, logger=self.logger)
        compiled = expr.compile()
        self.assertEqual(compiled, "(regex1 regex2)")

    def test_compile_with_or_type(self):
        data = {
            "name": "With OR",
            "type": "or",
            "pattern": [
                "regex1",
                {"pattern": "regex2"}
            ]
        }
        expr = Expression.new(data, logger=self.logger)
        compiled = expr.compile()
        self.assertEqual(compiled, "(regex1|regex2)")

    def test_invalid_type_defaults_to_and(self):
        expr = Expression.new("regex", type="invalid", logger=self.logger)
        self.assertEqual(expr.type, "and")

    def test_invalid_data_raises_error(self):
        with self.assertRaises(ValueError):
            Expression.new(12345, logger=self.logger)

    def test_invalid_pattern_raises_error(self):
        with self.assertRaises(ValueError):
            Expression.new({"pattern": 12345}, logger=self.logger)


if __name__ == "__main__":
    unittest.main()
