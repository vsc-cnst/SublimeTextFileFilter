import sys
import os

import sublime

import unittest
from unittest import TestCase
from unittest.mock import patch

enums = sys.modules["File Filter.utils.enums"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes


class TestCommandFilter_File1(unittest.TestCase):

    def test_members(self):
        expected_members = ['line', 'match_only', 'before_only', 'after_only', 'highlight_only']
        self.assertEqual([member.name for member in FoldingTypes], expected_members)
    
    def test_all_members(self):
        expected_members = ['line', 'match_only', 'before_only', 'after_only', 'highlight_only']
        self.assertEqual(FoldingTypes.all_members(), expected_members)

    def test_descriptions(self):
        expected_members = ['Line','Match only','Fold before','Fold after','Highlight only']
        self.assertEqual(FoldingTypes.all_values(), expected_values)

    def test_match(self):
        expected_keys = ['line', 'match_only', 'before_only', 'after_only', 'highlight_only']
        expected_values = ['Line','Match only','Fold before','Fold after','Highlight only']
        for (key, val) in zip(expected_keys, expected_values):
            self.assertEqual(FoldingTypes[key].value, val)


class TestCommandFilter_File1(unittest.TestCase):

    def test_members(self):
        expected_members = ['outline', 'solid', 'underline_solid', 'underline_stippled', 'underline_squiggly', 'none']
        self.assertEqual([member.name for member in HighlightTypes], expected_members)

    def test_all_members(self):
        self.assertEqual(HighlightTypes.all_members(), list(HighlightTypes))

    def test_values(self):
        expected_values = [
            sublime.DRAW_NO_FILL, 
            sublime.DRAW_NO_OUTLINE, 
            sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE,
            sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE,
            sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE,
            sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
        ]
        self.assertEqual(HighlightTypes.all_values(), expected_values)

    def test_descriptions(self):
        expected_descriptions = ['Outline', 'Solid', 'Underline solid', 'Underline stippled', 'Underline squiggly', 'None']
        self.assertEqual(HighlightTypes.all_descriptions(), expected_descriptions)


    def test_value_description_match(self):
        expected_data = [
            ('outline', 'Outline', sublime.DRAW_NO_FILL),
            ('solid', 'Solid', sublime.DRAW_NO_OUTLINE),
            ('underline_solid', 'Underline solid', sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE),
            ('underline_stippled', 'Underline stippled', sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE),
            ('underline_squiggly', 'Underline squiggly', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE),
            ('none', 'None', sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
        ]
        for member, (expected_name, expected_desc, expected_value) in zip(HighlightTypes, expected_data):
            self.assertEqual(member.name, expected_name)
            self.assertEqual(member.description, expected_desc)
            self.assertEqual(member._value_, expected_value)













