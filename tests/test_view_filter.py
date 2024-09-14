import sys
import os

import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes

class TestViewCommandFilter(TestCase):

    @classmethod
    def setUp(cls):
        cls.window = sublime.active_window()
        cls.view = cls.window.new_file()
        cls.window.focus_view(cls.view)

        cls.mock_logger = MagicMock()

        if not hasattr(cls, 'file') or not cls.file:
            raise ValueError("File content is not set")

        cls.view.run_command("insert", {"characters": cls.file})

        cls.view_size = cls.view.size()
        cls.view_lines = cls.view.lines(sublime.Region(0, cls.view_size))
  
    @classmethod
    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
        
    def run_filter(self, regex, folding_types, expected_values):

        settings = sublime.Settings(0)
        view_utils.set_folding_type(self.mock_logger, self.view, settings, folding_types)
        self.assertEqual(view_utils.get_folding_type(self.mock_logger, self.view, settings), folding_types)
        
        view_utils.filter(self.mock_logger, self.view, regex, folding_types, HighlightTypes.solid)

        actual_values = [r.to_tuple() for r in self.view.folded_regions()]
        self.assertEqual(actual_values, expected_values)


class TestViewFilterOnFile1(TestCommandFilter):     

    @classmethod
    def setUpClass(self):
        current_package_path = os.path.dirname(__file__)
        self.file = open(os.path.join(current_package_path, 'fixtures', "example_text_case_1.txt")).read()

    def test_show_line_only(self):
        self.run_filter(r"[0-9]", FoldingTypes.line, [(0, 3), (7, 11), (15, 19)])

    def test_show_match_only(self):
        self.run_filter(r"[0-9]", FoldingTypes.match_only, [(0, 3), (4, 5), (6, 11), (12, 13), (14, 19), (20, 21), (22, 23), (24, 25)])

    def test_fold_before_only(self):
        self.run_filter(r"[0-9]", FoldingTypes.before_only, [(0, 5), (8, 13), (16, 21)])

    def test_fold_after_only(self):
        self.run_filter(r"[0-9]", FoldingTypes.after_only, [(0, 3) , (6, 11), (14, 19), (24, 25)])


class TestViewFilterOnFile2(TestCommandFilter):

    @classmethod
    def setUpClass(self):
        current_package_path = os.path.dirname(__file__)
        self.file = open(os.path.join(current_package_path, 'fixtures', "example_text_case_2.txt")).read()

    def test_show_line_only(self):
        self.run_filter(r"[0-9]", FoldingTypes.line, [(0, 7), (11, 15), (19, 23), (30, 34)])
