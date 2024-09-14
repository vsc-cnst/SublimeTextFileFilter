import sys
import unittest
import sublime

from unittest.mock import MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]

HighlightTypes = enums.HighlightTypes

class TestViewHighlightType(unittest.TestCase):

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
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, 999)
        expected_result = HighlightTypes.solid
        self.validate(set_result, expected_result)

    @unittest.skip("valor das self.settings parece não estar a ser usado durante os testes automáticos")
    def test_settings_invalid_input(self):
        self.settings.set("default_highlight_type", "underline_squiggly")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, 9999)
        expected_result = HighlightTypes.underline_squiggly
        self.validate(set_result, expected_result)

    def test_NO_settings_file(self):
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, None)
        expected_result = HighlightTypes.solid
        self.validate(set_result, expected_result)

    @unittest.skip("valor das self.settings parece não estar a ser usado durante os testes automáticos")
    def test_settings_file_use_fallback_underline_squiggly(self):
        self.settings.set("default_highlight_type", "underline_squiggly")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, None)
        expected_result = HighlightTypes.underline_squiggly
        self.validate(set_result, expected_result)

    @unittest.skip("valor das self.settings parece não estar a ser usado durante os testes automáticos")
    def test_settings_file_use_fallback_none(self):
        self.settings.set("default_highlight_type", "none")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, None)
        expected_result = HighlightTypes.none
        self.validate(set_result, expected_result)

    def test_settings_file_do_NOT_use_fallback(self):
        self.settings.set("default_highlight_type", "solid")
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, HighlightTypes.underline_squiggly)
        expected_result = HighlightTypes.underline_squiggly
        self.validate(set_result, expected_result)

    def test_set_none(self):
        self.assertEqual(None, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, None)
        expected_result = HighlightTypes.solid
        self.validate(set_result, expected_result)

    def test_set_str(self):
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, HighlightTypes.underline_squiggly.name)
        expected_result = HighlightTypes.underline_squiggly
        self.validate(set_result, expected_result)

    def test_set_highlight_type_underline_squiggly_enum(self):
        set_result = view_utils.set_highlight_type(self.mock_logger, self.view, self.settings, HighlightTypes.underline_squiggly)
        expected_result = HighlightTypes.underline_squiggly
        self.validate(set_result, expected_result)

    def validate(self, result_highlight_type: HighlightTypes, expected_highlight_type: HighlightTypes):
        self.assertEqual(result_highlight_type, expected_highlight_type)
        self.assertEqual(result_highlight_type.name, self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, None))
        self.assertEqual(result_highlight_type, view_utils.get_highlight_type(self.mock_logger, self.view, self.settings))
