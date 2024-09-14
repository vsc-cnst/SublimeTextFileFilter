import sys
import unittest
import sublime
import logging
from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes


class TestViewFoldingType(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
  
        self.mock_logger = MagicMock()
        self.settings = sublime.Settings(0)

    @classmethod
    def tearDown(self):

        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_NO_settings_invalid_input(self):
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, 999)
        expected_result = FoldingTypes.line
        self.validate(set_result, expected_result)

    @unittest.skip("valor das self.settings parece não estar a ser usado durante os testes automáticos")
    def test_settings_invalid_input(self):
        self.settings.set("default_folding_type", "match_only")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, 9999)
        expected_result = FoldingTypes.match_only
        self.validate(set_result, expected_result)

    def test_NO_settings_file(self):
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, None)
        expected_result = FoldingTypes.line
        self.validate(set_result, expected_result)

    @unittest.skip("valor das self.settings parece não estar a ser usado durante os testes automáticos")
    def test_settings_file_use_fallback_match_only(self):
        self.settings.set("default_folding_type", "match_only")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, None)
        expected_result = FoldingTypes.match_only
        self.validate(set_result, expected_result)

    @unittest.skip("valor das self.settings parece não estar a ser usado durante os testes automáticos")
    def test_settings_file_use_fallback_highlight_only(self):
        self.settings.set("default_folding_type", "highlight_only")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, None)
        expected_result = FoldingTypes.highlight_only
        self.validate(set_result, expected_result)

    def test_settings_file_do_NOT_use_fallback(self):
        self.settings.set("default_folding_type", "line")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, FoldingTypes.match_only)
        expected_result = FoldingTypes.match_only
        self.validate(set_result, expected_result)

    def test_set_none(self):
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, None)
        expected_result = FoldingTypes.line
        self.validate(set_result, expected_result)

    def test_set_str(self):
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, FoldingTypes.match_only.name)
        expected_result = FoldingTypes.match_only
        self.validate(set_result, expected_result)

    def test_set_folding_type_match_only_enum(self):
        set_result = view_utils.set_folding_type(self.mock_logger, self.view, self.settings, FoldingTypes.match_only)
        expected_result = FoldingTypes.match_only
        self.validate(set_result, expected_result)

    def validate(self, result_folding_type: FoldingTypes, expected_folding_type: FoldingTypes):
        self.assertEqual(result_folding_type, expected_folding_type)
        self.assertEqual(result_folding_type.name, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE, None))
        self.assertEqual(result_folding_type, view_utils.get_folding_type(self.mock_logger, self.view, self.settings))

