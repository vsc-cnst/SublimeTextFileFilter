import sys
import sublime # type: ignore
import unittest
from unittest.mock import MagicMock, patch


File_Filter = sys.modules["File Filter.file_filter"]
SetFoldingTypeCommand = File_Filter.SetFoldingTypeCommand

FoldingTypesInputHandler = File_Filter.FoldingTypesInputHandler


enums = sys.modules["File Filter.utils.enums"]
FoldingTypes = enums.FoldingTypes

view_utils = sys.modules["File Filter.utils.view"]

class TestSetFoldingTypeCommand(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
  
        self.command = SetFoldingTypeCommand(self.view)
        self.command.logger = MagicMock()

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

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)
        self.handler = FoldingTypesInputHandler(view=self.view, logger=MagicMock())
        self.handler.logger = MagicMock()

    def tearDown(self):
        self.view.set_scratch(True)
        self.window.focus_view(self.view)
        self.view.window().run_command("close_file")

    def test_name(self):
        self.assertEqual(self.handler.name(), "folding_types")

    def test_list_items(self):
        self.assertEqual(self.handler.list_items(), [(ft.value, ft.name) for ft in FoldingTypes.all_members()])

    @patch.object(view_utils, "filter")
    def test_confirm_sets_type_and_refilters(self, mock_filter):
        self.handler.confirm(FoldingTypes.match_only.name)

        self.assertEqual(
            self.view.settings().get(view_utils.VIEW_SETTINGS_CURRENT_FOLDING_TYPE),
            FoldingTypes.match_only.name,
        )

        mock_filter.assert_called_once_with(
            self.handler.logger,
            self.view,
            None,
            FoldingTypes.match_only,
            view_utils.get_highlight_type(self.handler.logger, self.view, self.handler.settings),
        )


