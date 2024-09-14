import sys
import unittest
import sublime
import logging
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes


class TestViewRegex(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
  
        self.mock_logger = MagicMock()

    @classmethod
    def tearDown(self):

        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_no_regex(self):
        result = view_utils.get_current_regex(self.mock_logger, self.view, None)
        self.assertEqual(result, None)

    def test_set_current_regex(self):
        expected_regex = "TestViewRegex.test_set_current_regex.regex"
        view_utils.set_current_regex(self.mock_logger, self.view, None, expected_regex)
        current_view_regex = self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_REGEX, None)
        
        self.assertEqual(expected_regex, current_view_regex)

    def test_get_current_regex(self):
        initial_regex = "TestViewRegex.test_get_current_regex.regex"
        view_utils.set_current_regex(self.mock_logger, self.view, None, initial_regex)
        
        result = view_utils.get_current_regex(self.mock_logger, self.view, None)

        self.assertEqual(result, initial_regex)
