import sys
import unittest
import sublime  # type: ignore
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]
SettingsSnapshot = sys.modules["File Filter.utils.settings_manager"].SettingsSnapshot

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes


class TestViewFoldingType(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
        self.mock_logger = MagicMock()
        self.settings = self.make_settings_snapshot("line")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_invalid_value_uses_nested_default(self):
        self.settings = self.make_settings_snapshot("match_only")

        result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, 999)

        self.assert_folding_type(result, FoldingTypes.match_only)

    def test_none_uses_nested_default(self):
        self.settings = self.make_settings_snapshot("highlight_only")

        result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings)

        self.assert_folding_type(result, FoldingTypes.highlight_only)

    def test_accepts_member_name(self):
        result = view_utils.set_folding_type(
            self.mock_logger,
            self.view,
            self.settings,
            FoldingTypes.before_only.name,
        )

        self.assert_folding_type(result, FoldingTypes.before_only)

    def test_accepts_enum_member(self):
        result = view_utils.set_folding_type(
            self.mock_logger,
            self.view,
            self.settings,
            FoldingTypes.after_only,
        )

        self.assert_folding_type(result, FoldingTypes.after_only)

    def test_get_uses_current_view_type(self):
        self.view.settings().set(
            view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE,
            FoldingTypes.match_only.name,
        )

        result = view_utils.get_folding_type(self.mock_logger, self.view, self.settings)

        self.assertEqual(result, FoldingTypes.match_only)

    def make_settings_snapshot(self, folding_type):
        sublime_settings = MagicMock()
        values = {
            "defaults": {
                "folding": {"type": folding_type},
                "highlight": {},
            }
        }
        sublime_settings.get.side_effect = lambda key, default=None: values.get(key, default)
        return SettingsSnapshot(sublime_settings)

    def assert_folding_type(self, result, expected):
        self.assertEqual(result, expected)
        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE),
            expected.name,
        )

