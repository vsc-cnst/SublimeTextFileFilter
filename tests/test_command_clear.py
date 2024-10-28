import sys
import os
import sublime  # type: ignore
import unittest
from unittest.mock import patch, MagicMock

enums = sys.modules["File Filter.utils.enums"]
view_utils = sys.modules["File Filter.utils.view"]
File_Filter = sys.modules["File Filter.file_filter"]

FoldingTypes = enums.FoldingTypes
HighlightTypes = enums.HighlightTypes

ClearCommand = File_Filter.ClearCommand

class TestClearCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.window = MagicMock()
        cls.view = MagicMock()
        cls.window.active_view.return_value = cls.view

        cls.command = ClearCommand(cls.window)
        cls.command.logger = MagicMock()

    @classmethod
    def tearDownClass(cls):
        cls.view = None
        cls.window = None

    @patch('File Filter.file_filter.view_utils.clear')
    def test_run(self, mock_clear):
        self.command.run()
        mock_clear.assert_called_once_with(
            self.command.logger,
            self.view,
            unfold_regions=True,
            remove_highlights=True,
            center_viewport_on_carret=True
        )

    @unittest.skip("problemas com o MagicMock")
    @patch('File Filter.file_filter.view_utils.clear')
    def test_run_with_file(self, mock_clear):
        mock_logger = MagicMock()
        current_package_path = os.path.dirname(__file__)
        file_path = os.path.join(current_package_path, 'fixtures', "example_text_case_1.txt")
        
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        self.view.run_command("insert", {"characters": file_content})
        self.assertGreater(self.view.view_size(), 0, "View must have content")

        self.assertEqual(len(self.view.folded_regions()), 0, "View must start with no folded regions")
        view_utils.filter(mock_logger, self.view, r"[0-9]", FoldingTypes.line, HighlightTypes.solid)
        self.assertGreater(len(self.view.folded_regions()), 0, "No folded regions after filter")

        self.command.run()
        mock_clear.assert_called_once_with(
            self.command.logger,
            self.view,
            unfold_regions=True,
            remove_highlights=True,
            center_viewport_on_carret=True
        )

        self.assertEqual(len(self.view.folded_regions()), 0)