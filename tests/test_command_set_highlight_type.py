import sys
import sublime  # type: ignore
import unittest
from unittest.mock import ANY, MagicMock, patch

File_Filter = sys.modules["File Filter.file_filter"]
enums = sys.modules["File Filter.utils.enums"]

HighlightTypes = enums.HighlightTypes

SetHighlightTypeCommand = File_Filter.SetHighlightTypeCommand
HighlightTypesInputHandler = File_Filter.HighlightTypesInputHandler

class TestSetHighlightTypeCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.window = sublime.active_window()
        cls.view = cls.window.new_file()
        cls.window.focus_view(cls.view)
  
        cls.command = SetHighlightTypeCommand(cls.view)
        cls.command.logger = MagicMock()

    @classmethod
    def tearDownClass(cls):
        if cls.view:
            cls.view.set_scratch(True)
            cls.window.focus_view(cls.view)
            cls.view.window().run_command("close_file")

    def test_run(self):
        edit = MagicMock()
        self.command.run(edit, highlight_types=HighlightTypes.solid.name)
        self.command.logger.debug.assert_called_with(highlight_types=HighlightTypes.solid.name)

    def test_handler(self):
        result = self.command.input({'some_arg': 'value'})
        self.assertIsInstance(result, HighlightTypesInputHandler)


class TestHighlightTypesInputHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.window = sublime.active_window()
        cls.view = cls.window.new_file()
        cls.window.focus_view(cls.view)

        cls.mock_logger = MagicMock()

        cls.handler = HighlightTypesInputHandler(view=cls.view, settings_file="fake_settings_file_name", logger=MagicMock())

    @classmethod
    def tearDownClass(cls):
        if cls.view:
            cls.view.set_scratch(True)
            cls.window.focus_view(cls.view)
            cls.view.window().run_command("close_file")

    def test_name(self):
        self.assertEqual(self.handler.name(), "highlight_types")

    def test_list_items(self):
        self.assertEqual(self.handler.list_items(), [(ft.description, ft.name) for ft in HighlightTypes.all_members()])

    @unittest.skip("TODO has error")
    @patch('File Filter.utils.view.set_highlight_type')
    @patch('File Filter.utils.view.filter')
    def test_confirm(self, mock_filter, mock_set_highlight_type):
        self.handler.confirm('Test HighlightTypes Name')

        mock_set_highlight_type.assert_called_with(ANY, ANY, ANY, 'Test HighlightTypes Name')
        mock_filter.assert_called_once_with(ANY, ANY, ANY, ANY, ANY)
