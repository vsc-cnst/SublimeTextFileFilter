import sys
import unittest
import sublime
import logging
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]


class TestViewAddToHistory(unittest.TestCase):

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

    def test_initial_state(self):
        self.assertEqual(self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY, None), None, "New view cannot have history")

    def test_initial_state(self):
        h_item = "history_item_1"
        expected_result = [h_item]
        result = view_utils.add_to_history(self.mock_logger, self.view, h_item)
        self.assertEqual(self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY, None), expected_result, "History must contain only one element")

    def test_initial_state(self):
        expected_result = [f"history_item_{i}" for i in range(1,100)]

        for i in expected_result:
            view_utils.add_to_history(self.mock_logger, self.view, i)
        
        result = self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY, expected_result)

        self.assertEqual(result, expected_result[::-1], None)