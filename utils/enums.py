import sublime # type: ignore
from enum import Enum


class MyEnum(Enum):

    @classmethod
    def all_members(cls):
        return [member for member in cls]

    @classmethod
    def all_values(cls):
        return [member._value_ for member in cls]


class FoldingTypes(MyEnum):

    line = 'Line'
    match_only = 'Match only'
    before_only = 'Fold before'
    after_only = 'Fold after'
    highlight_only = 'Highlight only'


class HighlightTypes(MyEnum):

    def __new__(cls, description, value):
        obj = object.__new__(cls)

        obj._value_ = value
        obj.description = description

        return obj

    @classmethod
    def all_descriptions(cls):
        return [member.description for member in cls]

    # Flags for how to draw the regions
    outline = 'Outline', sublime.DRAW_NO_FILL
    solid = 'Solid', sublime.DRAW_NO_OUTLINE 
    underline_solid = 'Underline solid', sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_stippled = 'Underline stippled', sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_squiggly= 'Underline squiggly', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    none = 'None', sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE


