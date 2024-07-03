import sys
import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch

from file_filter import FileFilterCommand
from file_filter import FoldingTypes
from file_filter import HighlightTypes

class TestCommandFilter(TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window .new_file()
        self.window.focus_view(self.view)

        self.command = FileFilterCommand(self.window)

        self.expected_options = [
            ['prompt', '___prompt___'], 
            ['clear', '___clear___'], 
            ['batch : [Step]', '\\[Step\\].*(?=\\{)'], 
            ['batch : [Step] IdProcesso', '\\[Step\\].*IdProcesso\\(.*(?=\\{)'], 
            ['batch : Starting w/ Date Time', '[0-9][0-9][0-9][0-9]\\-[0-9][0-9]\\-[0-9][0-9]\\ [0-9][0-9]\\:[0-9][0-9]\\:[0-9][0-9] \\['], 
            ["web : SOAP Request : HH", "(?s)<\\?xml.*?</s:Envelope>"],
        ]

        file_content = """2024-06-24 09:05:00 [INF] (0000000008) <Serilog.AspNetCore.RequestLoggingMiddleware> HTTP GET /index.html responded 200 in 327.7153 ms {}
2024-06-24 10:05:00 [INF] (0000000013) <Serilog.AspNetCore.RequestLoggingMiddleware> HTTP GET /index.html responded 200 in 334.1519 ms {}
2025-06-24 09:05:00 [INF] (0000000010) <Serilog.AspNetCore.RequestLoggingMiddleware> HTTP GET /index.html responded 200 in 340.1215 ms {}"""

        self.view.run_command("insert", {"characters": file_content})


    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
 

    @patch('sublime.Window.show_quick_panel')
    def test_filter_show_quick_panel(self, mock_show_quick_panel):
        
        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            on_select(3)

        mock_show_quick_panel.side_effect = quick_panel_callback

        self.command.run()

        mock_show_quick_panel.assert_called("Quick panenel not called")

        # Validate the arguments passed to show_quick_panel
        actual_args, actual_kwargs = mock_show_quick_panel.call_args
        actual_options = actual_args[0]

        self.assertEqual(actual_options,self.expected_options, "Unexpected set of options")

    @patch('sublime.Window.show_input_panel')
    @patch('sublime.Window.show_quick_panel')
    def test_filter_show_quick_panel_option_prompt_regex_empt(self, mock_show_quick_panel, mock_show_input_panel):

        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            # option '___prompt___'
            on_select(0)

        mock_show_quick_panel.side_effect = quick_panel_callback

        # Run the command which should call show_quick_panel
        self.command.run()

        mock_show_input_panel.assert_called_once_with('Enter  regex:', '', self.command.set_regex, None, None)


    @unittest.skip("TODO")
    @patch('sublime.Window.show_input_panel')
    @patch('sublime.Window.show_quick_panel')
    def test_filter_show_quick_panel_option_prompt_regex_value(self, mock_show_quick_panel, mock_show_input_panel):

        def quick_panel_callback(items, on_select, flags=0, selected_index=-1, on_highlight= None, placeholder=None):
            # option '___prompt___'
            on_select(0)

        mock_show_quick_panel.side_effect = quick_panel_callback

        # Run the command which should call show_quick_panel
        self.command.run()
        self.command.set_regex(r'\[INF\] \(0000000013\)')

        mock_show_input_panel.assert_called_once_with('Enter  regex:', r'\[INF\] \(0000000013\)', self.command.set_regex, None, None)


    def test_filter_set_regex(self):
    
        self.command.run()
        self.command.set_regex(r'\[INF\] \(0000000013\)')

        self.assertEqual(len(self.view.folded_regions()), 2, "There must be 4 folded regions")

    def test_filter_folded_match_only(self):
        
        self.command.run()
        self.command.set_regex(r'\[INF\] \(0000000013\)')

        self.command.command_set_folding_type(FoldingTypes.match_only)

        self.assertEqual(len(self.view.folded_regions()), 4, "There must be 4 folded regions")

    def test_filter_folded_before_only_1(self):
        
        self.command.run()
        self.command.set_regex(r'\[INF\] \(0000000013\)')

        self.command.command_set_folding_type(FoldingTypes.before_only)

        self.assertEqual(len(self.view.folded_regions()), 3, "There must be 3 folded regions")

    def test_filter_folded_before_only_2(self):
        
        self.command.run()
        self.command.set_regex(r'^2025-06-24 09:05:00$')

        self.command.command_set_folding_type(FoldingTypes.before_only)

        self.assertEqual(len(self.view.folded_regions()), 2, "There must be 3 folded regions")

        # TODO : garantir que as regioes que estao folded sao as pretendidas

    def test_filter_folded_after_only_1(self):
        
        self.command.run()
        self.command.set_regex(r'\[INF\] \(0000000013\)')

        self.command.command_set_folding_type(FoldingTypes.after_only)

        self.assertEqual(len(self.view.folded_regions()), 3, "There must be 3 folded regions")
        
        # TODO : garantir que as regioes que estao folded sao as pretendidas

    def test_filter_folded_after_only_2(self):
        
        self.command.run()
        self.command.set_regex(r'2025\-06\-24 09\:05\:00')

        self.command.command_set_folding_type(FoldingTypes.after_only)

        self.assertEqual(len(self.view.folded_regions()), 1)


    @unittest.skip("TODO")
    def test_filter_change_views(self):
        pass


