import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

File_Filter = sys.modules["File Filter.file_filter"]
ClearCommand = File_Filter.ClearCommand


class TestClearCommand(unittest.TestCase):

    def setUp(self):
        self.window = MagicMock()
        self.view = MagicMock()
        self.window.active_view.return_value = self.view

        self.command = ClearCommand(self.window)
        self.command.logger = MagicMock()

    @patch.object(File_Filter.view_utils, "clear")
    def test_run_forwards_configured_options(self, mock_clear):
        self.command.settings.commands.clear = SimpleNamespace(
            unfold_regions=False,
            remove_highlights=True,
            center_viewport_on_carret=False,
        )

        self.command.run()
        mock_clear.assert_called_once_with(
            self.command.logger,
            self.view,
            unfold_regions=False,
            remove_highlights=True,
            center_viewport_on_carret=False,
        )