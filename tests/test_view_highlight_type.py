import sys
import unittest
import sublime
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]
SettingsSnapshot = sys.modules["File Filter.utils.settings_manager"].SettingsSnapshot

HighlightTypes = enums.HighlightTypes

class TestViewHighlightType(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
        self.mock_logger = MagicMock()
        self.settings = self.make_settings_snapshot("solid")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_invalid_value_uses_nested_default(self):
        self.settings = self.make_settings_snapshot("underline_squiggly")

        result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, 999)

        self.assert_highlight_type(result, HighlightTypes.underline_squiggly)

    def test_none_uses_nested_default(self):
        self.settings = self.make_settings_snapshot("none")

        result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings)

        self.assert_highlight_type(result, HighlightTypes.none)

    def test_accepts_member_name(self):
        result = view_utils.set_highlight_type(
            self.mock_logger,
            self.view,
            self.settings,
            HighlightTypes.outline.name,
        )

        self.assert_highlight_type(result, HighlightTypes.outline)

    def test_accepts_enum_member(self):
        result = view_utils.set_highlight_type(
            self.mock_logger,
            self.view,
            self.settings,
            HighlightTypes.underline_stippled,
        )

        self.assert_highlight_type(result, HighlightTypes.underline_stippled)

    def test_get_uses_current_view_type(self):
        self.view.settings().set(
            view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE,
            HighlightTypes.outline.name,
        )

        result = view_utils.get_highlight_type(self.mock_logger, self.view, self.settings)

        self.assertEqual(result, HighlightTypes.outline)

    def make_settings_snapshot(self, highlight_type):
        sublime_settings = MagicMock()
        values = {
            "defaults": {
                "folding": {},
                "highlight": {"type": highlight_type},
            }
        }
        sublime_settings.get.side_effect = lambda key, default=None: values.get(key, default)
        return SettingsSnapshot(sublime_settings)

    def assert_highlight_type(self, result, expected):
        self.assertEqual(result, expected)
        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE),
            expected.name,
        )
