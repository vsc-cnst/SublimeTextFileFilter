import logging
import re
from typing import List, Union


class Expression:
    def __init__(self, pattern: Union[str, dict, List[Union[str, dict]]], name: str = "", description: str = "", type: str = "and", color: str = "white", escape: bool = False):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        if type not in ['and', 'or']:
            type = 'and'

        self.name = name
        self.description = description
        self.type = type
        self.color = color
        self.escape = escape
        
        self.pattern = self._process_pattern(pattern)

        self.logger.debug(f"Expression initialized with name: {self.name}, description: {self.description}, type: {self.type}, pattern: {self.pattern}")

    def _process_pattern(self, pattern: Union[str, dict, List[Union[str, dict]]]) -> Union[str, List["Expression"]]:
        if isinstance(pattern, str):
            self.logger.debug("Processing string pattern")
            return re.escape(pattern) if self.escape else pattern
        elif isinstance(pattern, list):
            self.logger.debug("Processing list pattern")
            return [self._process_pattern(p) if isinstance(p, (str, dict)) else p for p in pattern]
        elif isinstance(pattern, dict):
            self.logger.debug("Processing dictionary pattern")
            return Expression.new(pattern, logger=self.logger)
        else:
            self.logger.error(f"Invalid pattern type: {type(pattern)}. Pattern must be a string, dictionary, or list")
            raise ValueError(f"Invalid pattern type: {type(pattern)}. Pattern must be a string, dictionary, or list")

    def compile(self) -> str:
        if isinstance(self.pattern, str):
            return f"({self.pattern})"
        elif isinstance(self.pattern, list):
            separator = "|" if self.type == "or" else ""
            compiled = f"({separator.join(p.compile() if isinstance(p, Expression) else p for p in self.pattern)})"
            self.logger.debug(f"Compiled Expression: {compiled}")
            return compiled
        raise ValueError("Invalid pattern format for compilation")

    @staticmethod
    def new(data: Union[str, dict, List[Union[str, dict]]], name: str = "", description: str = "", type: str = "and", color: str = "white", escape: bool = False, logger=None) -> "Expression":
        if logger is None:
            logger = logging.getLogger("Expression")

        logger.debug(f"Creating new Expression from data: {data}")
        
        if isinstance(data, str):
            return Expression(pattern=data, name=name, description=description, type=type, color=color, escape=escape)
        elif isinstance(data, dict):
            pattern = data.get("pattern", "")
            if isinstance(pattern, str):
                pass  # Use the pattern as-is
            elif isinstance(pattern, (dict, list)):
                pattern = Expression.new(pattern, logger=logger)

            return Expression(
                pattern=pattern,
                name=data.get("name", name),
                description=data.get("description", description),
                type=data.get("type", type),
                color=data.get("color", color),
                escape=data.get("escape", escape)
            )
        elif isinstance(data, list):
            return Expression(
                pattern=[Expression.new(p, logger=logger) if isinstance(p, (str, dict)) else p for p in data],
                name=name,
                description=description,
                type=type,
                color=color,
                escape=escape
            )
        else:
            logger.error(f"Invalid data type: {type(data)}. Data must be a string, dictionary, or list")
            raise ValueError(f"Invalid data type: {type(data)}. Data must be a string, dictionary, or list")

    def __repr__(self):
        return (f"Expression(name={self.name}, description={self.description}, "
                f"type={self.type}, pattern={self.pattern})")

# Examples of possible combinations for the `pattern` parameter in an Expression:
# 
# 1. A simple string pattern:
#    "regex"
#
# 2. A list of string patterns:
#    [
#        "regex",
#        "another_regex"
#    ]
#
# 3. A dictionary defining a pattern:
#    {
#        "name": "Basic Pattern",
#        "description": "Matches a basic pattern",
#        "type": "and",
#        "pattern": "regex"
#    }
#
# 4. A nested dictionary defining a pattern:
#    {
#        "name": "Nested Pattern",
#        "description": "Contains a nested pattern",
#        "type": "and",
#        "pattern": {
#            "name": "Inner Pattern",
#            "description": "The inner pattern",
#            "type": "or",
#            "pattern": "nested_regex"
#        }
#    }
#
# 5. A complex structure with mixed patterns:
#    {
#        "name": "Complex Pattern",
#        "description": "Combines various patterns",
#        "type": "and",
#        "pattern": [
#            "regex",
#            "another_regex",
#            {
#                "name": "Sub Pattern",
#                "description": "A sub-level pattern",
#                "type": "or",
#                "pattern": [
#                    "nested_regex",
#                    {
#                        "name": "Deep Nested",
#                        "description": "Deeply nested pattern",
#                        "type": "and",
#                        "pattern": "deep_nested_regex"
#                    }
#                ]
#            }
#        ]
#    }
