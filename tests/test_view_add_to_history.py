import sys
import unittest
import sublime
import logging
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]


class TestViewAddToHistory(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
        self.mock_logger = MagicMock()

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_history_starts_empty(self):
        self.assertEqual(self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY, None), None, "New view cannot have history")

    def test_adds_new_item_at_front(self):
        view_utils.add_to_history(self.mock_logger, self.view, "older")
        view_utils.add_to_history(self.mock_logger, self.view, "newer")

        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY),
            ["newer", "older"],
        )

    def test_ignores_empty_items(self):
        view_utils.add_to_history(self.mock_logger, self.view, "")

        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY),
            [],
        )

    def test_history_is_limited_to_100_items(self):
        for index in range(101):
            view_utils.add_to_history(self.mock_logger, self.view, f"item-{index}")

        history = self.view.settings().get(view_utils.VIEW_SETTINGS_REGEX_HISTORY)
        self.assertEqual(len(history), 100)
        self.assertEqual(history[0], "item-100")
        self.assertEqual(history[-1], "item-1")