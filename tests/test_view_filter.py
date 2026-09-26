import sys
import os

import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]
SettingsSnapshot = sys.modules["File Filter.utils.settings_manager"].SettingsSnapshot

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes

class TestViewCommandFilter(TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)

        self.mock_logger = MagicMock()

        if not hasattr(self, 'file') or not self.file:
            raise ValueError("File content is not set")

        self.view.run_command("insert", {"characters": self.file})

        self.view_size = self.view.size()
        self.view_lines = self.view.lines(sublime.Region(0, self.view_size))
  
    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
        
    def run_filter(self, regex, folding_types, expected_values):

        settings = SettingsSnapshot(sublime.load_settings("file_filter.sublime-settings"))
        view_utils.set_folding_type(self.mock_logger, self.view, settings, folding_types)
        self.assertEqual(view_utils.get_folding_type(self.mock_logger, self.view, settings), folding_types)
        
        view_utils.filter(self.mock_logger, self.view, regex, folding_types, HighlightTypes.solid)

        actual_values = [r.to_tuple() for r in self.view.folded_regions()]
        self.assertEqual(actual_values, expected_values)


class TestViewFilterOnFile1(TestViewCommandFilter):     

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

    def test_no_matches_produces_no_fold_or_highlight_regions(self):
        view_utils.filter(
            self.mock_logger,
            self.view,
            "no-such-text",
            FoldingTypes.line,
            HighlightTypes.solid,
        )

        self.assertEqual(self.view.folded_regions(), [])
        self.assertEqual(
            self.view.get_regions(view_utils.VIEW_SETTINGS_HIGHLIGHTED_REGIONS),
            [],
        )
        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_REGEX),
            "no-such-text",
        )

    def test_highlight_only_highlights_matches_without_folding(self):
        view_utils.filter(
            self.mock_logger,
            self.view,
            r"[0-9]",
            FoldingTypes.highlight_only,
            HighlightTypes.solid,
        )

        self.assertEqual(self.view.folded_regions(), [])
        self.assertEqual(
            self.view.get_regions(view_utils.VIEW_SETTINGS_HIGHLIGHTED_REGIONS),
            self.view.find_all(r"[0-9]"),
        )


class TestViewFilterOnFile2(TestViewCommandFilter):

    @classmethod
    def setUpClass(self):
        current_package_path = os.path.dirname(__file__)
        self.file = open(os.path.join(current_package_path, 'fixtures', "example_text_case_2.txt")).read()

    def test_show_line_only(self):
        self.run_filter(r"[0-9]", FoldingTypes.line, [(0, 7), (11, 15), (19, 23), (30, 34)])
