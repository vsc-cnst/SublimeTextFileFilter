import sys
import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch

file_filter = sys.modules["File Filter.file_filter"]


FileFilterPromptRegexCommand = file_filter.FileFilterPromptRegexCommand

FoldingTypes = file_filter.FoldingTypes
HighlightTypes = file_filter.HighlightTypes

class TestCommandFilter(TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)

        self.quick_panel_expected_options = [
            ['prompt', '___prompt___'], 
            ['clear', '___clear___'], 
            ['[INF]', '\\[INF[0-9]]'],
            ["Starting w/ Date Time", "[0-9][0-9][0-9][0-9]\\-[0-9][0-9]\\-[0-9][0-9]\\ [0-9][0-9]\\:[0-9][0-9]\\:[0-9][0-9] \\["]
        ]


    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
 

    # @unittest.skip("TODO")
    @patch('sublime.Window.show_quick_panel')
    @patch('sublime.Window.show_input_panel')
    def test_command_quick_panel_options(self, mock_show_quick_panel, show_input_panel):
        
        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            on_select(0)

        mock_show_quick_panel.side_effect = quick_panel_callback

        self.window.run_command('file_filter_quick_panel')

        mock_show_quick_panel.assert_called()

        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]

        self.assertEqual(actual_options,self.quick_panel_expected_options, "Unexpected set of options")



    @patch('sublime.Window.show_input_panel')
    @patch('sublime.Window.show_quick_panel')
    def test_command_quick_panel_options(self, mock_show_quick_panel, mock_show_input_panel):
        
        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight=None, placeholder=None):
            on_select(0)

        def input_panel_callback(caption, initial_text, on_done, on_change, on_cancel):
            on_done("test input")

        mock_show_quick_panel.side_effect = quick_panel_callback
        mock_show_input_panel.side_effect = input_panel_callback

        self.window.run_command('file_filter_quick_panel')

        mock_show_quick_panel.assert_called()

        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]
        self.assertEqual(actual_options, self.quick_panel_expected_options, "Unexpected set of options")

        mock_show_input_panel.assert_called()



    # @unittest.skip("TODO")
    @patch('sublime.Window.show_input_panel')
    def test_command_prompt_regex_open(self, mock_show_input_panel):

        self.window.run_command('file_filter_prompt_regex')

        mock_show_input_panel.assert_called_once_with("Enter regex:", "", unittest.mock.ANY, None, None)



    # @unittest.skip("TODO")
    @patch('sublime.Window.show_input_panel')
    def test_command_prompt_regex_set(self, mock_show_input_panel):

        def input_panel_callback(caption, initial_text, on_done=None, on_change=None, on_cancel=None):
            self.assertEqual(initial_text, "")
            on_done("__test__regex__")

        mock_show_input_panel.side_effect = input_panel_callback

        command = FileFilterPromptRegexCommand(self.window)
        command.run()

        mock_show_input_panel.assert_called()

        # Assert the input text was processed correctly
        command.regex = "__test__regex__"



    # @unittest.skip("TODO")
    @patch('sublime.Window.show_quick_panel')
    def test_command_set_folding_type_options(self, mock_show_quick_panel):

        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            on_select(0)

        mock_show_quick_panel.side_effect = quick_panel_callback

        self.window.run_command('file_filter_set_folding_type')

        mock_show_quick_panel.assert_called()

        # Validate the arguments passed to show_quick_panel
        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]

        self.assertEqual(actual_options,FoldingTypes.all_values(), "Unexpected set of options")


    # @unittest.skip("TODO")
    @patch('sublime.Window.show_quick_panel')
    def test_command__set_highlight_type(self, mock_show_quick_panel):

        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            on_select(0)

        mock_show_quick_panel.side_effect = quick_panel_callback

        self.window.run_command('file_filter_set_highlight_type')

        mock_show_quick_panel.assert_called()

        # Validate the arguments passed to show_quick_panel
        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]

        self.assertEqual(actual_options,HighlightTypes.all_descriptions(), "Unexpected set of options")