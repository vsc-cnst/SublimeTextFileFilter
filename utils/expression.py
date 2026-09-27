import logging
import re
from typing import List, Union


class Expression:

    pattern: Union[str, "Expression", List["Expression"]]

    code: str
    name: str
    type: str
    color: str
    escape: bool
    

    def __init__(self, pattern: Union[str, dict, "Expression", List[Union[str, dict, "Expression"]]], code: str = "", name: str = "", type: str = "and", color: str = "white", escape: bool = False, logger=None):
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")

        if type not in ['and', 'or']:
            type = 'and'

        self.code = code
        self.name = name
        self.type = type
        self.color = color
        self.escape = escape
        
        self.pattern = self._process_pattern(pattern)

        self.logger.debug(f"Expression initialized with code: {self.code}, name: {self.name}, type: {self.type}, pattern: {self.pattern}")

    def _process_pattern(self, pattern: Union[str, dict, "Expression", List[Union[str, dict, "Expression"]]]) -> Union[str, "Expression", List["Expression"]]:
        if isinstance(pattern, str):
            self.logger.debug("Processing string pattern")
            return re.escape(pattern) if self.escape else pattern
        elif isinstance(pattern, Expression):
            return pattern
        elif isinstance(pattern, list):
            self.logger.debug("Processing list pattern")
            return [Expression.new(p, escape=self.escape, logger=self.logger) for p in pattern]
        elif isinstance(pattern, dict):
            self.logger.debug("Processing dictionary pattern")
            return Expression.new(pattern, logger=self.logger)
        else:
            self.logger.error(f"Invalid pattern type: {type(pattern)}. Pattern must be a string, dictionary, or list")
            raise ValueError(f"Invalid pattern type: {type(pattern)}. Pattern must be a string, dictionary, or list")

    def compile(self) -> str:
        if isinstance(self.pattern, str):
            return f"({self.pattern})"
        elif isinstance(self.pattern, Expression):
            return self.pattern.compile()
        elif isinstance(self.pattern, list):
            separator = "|" if self.type == "or" else ""
            compiled = f"({separator.join(p.compile() if isinstance(p, Expression) else p for p in self.pattern)})"
            self.logger.debug(f"Compiled Expression: {compiled}")
            return compiled
        raise ValueError("Invalid pattern format for compilation")

    @staticmethod
    def new(data: Union[str, dict, "Expression", List[Union[str, dict, "Expression"]]], code: str = "", name: str = "", type: str = "and", color: str = "white", escape: bool = False, logger=None) -> "Expression":
        if isinstance(data, Expression):
            return data

        if logger is None:
            logger = logging.getLogger(f"Expression_{code}")

        logger.debug(f"Creating new Expression from data: {data}")
        
        if isinstance(data, str):
            return Expression(pattern=data, code=code, name=name, type=type, color=color, escape=escape, logger=logger)
        elif isinstance(data, dict):
            pattern = data.get("pattern", "")
            return Expression(
                pattern=pattern,
                code=data.get("code", code),
                name=data.get("name", name),
                type=data.get("type", type),
                color=data.get("color", color),
                escape=data.get("escape", escape),
                logger=logger
            )
        elif isinstance(data, list):
            return Expression(
                pattern=data,
                name=name,
                code=code,
                type=type,
                color=color,
                escape=escape,
                logger=logger
            )
        else:
            raise ValueError(f"Invalid data type of value: '{data}'. Data must be a string, dictionary, or list")

    def __repr__(self):
        return (f"Expression(code={self.code}, name={self.name}, "
            f"type={self.type}, pattern={self.pattern})"
        )

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
#        "code": "basic-pattern",
#        "name": "Matches a basic pattern",
#        "type": "and",
#        "pattern": "regex"
#    }
#
# 4. A nested dictionary defining a pattern:
#    {
#        "code": "nested-pattern",
#        "name": "Contains a nested pattern",
#        "type": "and",
#        "pattern": {
#            "code": "inner-pattern",
#            "name": "The inner pattern",
#            "type": "or",
#            "pattern": "nested_regex"
#        }
#    }
#
# 5. A complex structure with mixed patterns:
#    {
#        "code": "complex-pattern",
#        "name": "Combines various patterns",
#        "type": "and",
#        "pattern": [
#            "regex",
#            "another_regex",
#            {
#                "code": "sub-pattern",
#                "name": "A sub-level pattern",
#                "type": "or",
#                "pattern": [
#                    "nested_regex",
#                    {
#                        "code": "deep-nested",
#                        "name": "Deeply nested pattern",
#                        "type": "and",
#                        "pattern": "deep_nested_regex"
#                    }
#                ]
#            }
#        ]
#    }
