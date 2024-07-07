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

class TestCommandPrompt(TestCase):

    def setUp(self): 
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)

        patch('File_Filter.file_filter.VIEW_SETTINGS_VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE', "DUMMY_VALUE")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
 

    @patch('sublime.Window.show_input_panel')
    @patch('sublime.Window.show_quick_panel')
    def test_command_quick_panel(self, mock_show_quick_panel, mock_show_input_panel):
        
        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight=None, placeholder=None):
            on_select(0)

        def input_panel_callback(caption, regex, on_done=None, on_change=None, on_cancel=None):
            
            actual_value = regex
            expected_value = ''
            self.assertEqual(actual_value, expected_value)

            on_done(regex)

        mock_show_quick_panel.side_effect = quick_panel_callback
        mock_show_input_panel.side_effect = input_panel_callback

        #run
        self.window.run_command('file_filter_quick_panel')

        mock_show_quick_panel.assert_called()
        mock_show_input_panel.assert_called()

        # quick pannel
        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]

        self.assertGreaterEqual(len(actual_options), 2)
        self.assertEqual(['prompt', '___prompt___'], actual_options[0], "Mandatory option in fst position")
        self.assertIn(['clear', '___clear___'], actual_options)


            
    @patch('sublime.Window.show_input_panel')
    def test_command_prompt_regex_open(self, mock_show_input_panel):

        self.window.run_command('file_filter_prompt_regex')

        mock_show_input_panel.assert_called_once_with("Enter regex:", "", unittest.mock.ANY, None, None)



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


    @patch('sublime.Window.show_quick_panel')
    def test_command_set_highlight_type(self, mock_show_quick_panel):

        def quick_panel_callback(items, on_select=None, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            on_select(0)

        mock_show_quick_panel.side_effect = quick_panel_callback

        self.window.run_command('file_filter_set_highlight_type')

        mock_show_quick_panel.assert_called_once_with(HighlightTypes.all_descriptions(), on_select=unittest.mock.ANY)

        # Validate the arguments passed to show_quick_panel
        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]

        self.assertEqual(actual_options,HighlightTypes.all_descriptions(), "Unexpected set of options")