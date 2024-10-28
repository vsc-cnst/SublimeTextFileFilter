import sys
import sublime # type: ignore
import unittest
from unittest.mock import MagicMock
import unittest
from unittest.mock import ANY, MagicMock, patch


File_Filter = sys.modules["File Filter.file_filter"]
SetFoldingTypeCommand = File_Filter.SetFoldingTypeCommand

FoldingTypesInputHandler = File_Filter.FoldingTypesInputHandler


enums = sys.modules["File Filter.utils.enums"]
FoldingTypes = enums.FoldingTypes

view_utils = sys.modules["File Filter.utils.view"]

class TestSetFoldingTypeCommand(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
  
        self.command = SetFoldingTypeCommand(self.view)
        self.command.logger = MagicMock()

    @classmethod
    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_run(self):
        edit = MagicMock()
        self.command.run(edit, folding_types=FoldingTypes.match_only.name)
        self.command.logger.debug.assert_called_with(folding_types=FoldingTypes.match_only.name)

    def test_handler(self):
        result = self.command.input({'some_arg': 'value'})
        self.assertIsInstance(result, FoldingTypesInputHandler)


class TestSetFoldingTypeInputHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.window = sublime.active_window()
        cls.view = cls.window.new_file()
        cls.window.focus_view(cls.view)

        
        cls.handler = FoldingTypesInputHandler(view=cls.view, settings_file="file_filter.sublime-settings", logger=MagicMock())
        cls.handler.logger = MagicMock()

    @classmethod
    def tearDownClass(cls):
        if cls.view:
            cls.view.set_scratch(True)
            cls.window.focus_view(cls.view)
            cls.view.window().run_command("close_file")

    def test_name(self):
        self.assertEqual(self.handler.name(), "folding_types")

    def test_list_items(self):
        self.assertEqual(self.handler.list_items(), [(ft.value, ft.name) for ft in FoldingTypes.all_members()])

    @patch('File Filter.utils.view.set_folding_type')
    @patch('File Filter.utils.view.filter')
    def test_confirm(self, mock_filter, mock_set_folding_type):
        
        self.handler.confirm('Test FoldingTypes Name')

        result = self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE)
        self.assertEqual(result, 'Test FoldingTypes Name')

        mock_filter.assert_called_once_with(ANY, ANY, ANY, ANY, ANY)


