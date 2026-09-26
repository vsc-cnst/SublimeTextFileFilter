import sys
import sublime  # type: ignore
import unittest
from unittest.mock import MagicMock, patch

File_Filter = sys.modules["File Filter.file_filter"]
view = sys.modules["File Filter.utils.view"]
enums = sys.modules["File Filter.utils.enums"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes

SetHighlightTypeCommand = File_Filter.SetHighlightTypeCommand
HighlightTypesInputHandler = File_Filter.HighlightTypesInputHandler
view_utils = sys.modules["File Filter.utils.view"]

class TestSetHighlightTypeCommand(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
        self.command = SetHighlightTypeCommand(self.view)
        self.command.logger = MagicMock()

    def tearDown(self):
        self.view.set_scratch(True)
        self.window.focus_view(self.view)
        self.view.window().run_command("close_file")

    def test_run(self):
        edit = MagicMock()
        self.command.run(edit, highlight_types=HighlightTypes.solid.name)
        self.command.logger.debug.assert_called_with(highlight_types=HighlightTypes.solid.name)

    def test_handler(self):
        result = self.command.input({'some_arg': 'value'})
        self.assertIsInstance(result, HighlightTypesInputHandler)


class TestHighlightTypesInputHandler(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
        self.handler = HighlightTypesInputHandler(view=self.view, logger=MagicMock())

    def tearDown(self):
        self.view.set_scratch(True)
        self.window.focus_view(self.view)
        self.view.window().run_command("close_file")

    def test_name(self):
        self.assertEqual(self.handler.name(), "highlight_types")

    def test_list_items(self):
        self.assertEqual(self.handler.list_items(), [(ft.description, ft.name) for ft in HighlightTypes.all_members()])

    @patch.object(view,'filter')
    def test_confirm_sets_type_and_refilters(self, mock_filter):
        self.handler.settings.defaults.folding.type = FoldingTypes.line.name
        self.handler.confirm(HighlightTypes.underline_squiggly.name)

        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE),
            HighlightTypes.underline_squiggly.name,
        )
        mock_filter.assert_called_once_with(
            self.handler.logger,
            self.view,
            None,
            FoldingTypes.line,
            HighlightTypes.underline_squiggly,
        )
