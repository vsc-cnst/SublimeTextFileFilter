import sublime
import sys
import unittest
from unittest import TestCase
from unittest.mock import patch
from file_filter import FileFilterClearCommand

class TestCommandClear(TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window .new_file()
        self.window.focus_view(self.view)

        self.command = FileFilterClearCommand(self.window)

        # self.view = self.window .new_file()
        # self.window.focus_view(self.view)

        file_content = """
2024-06-24 09:05:00 [INF] (0000000008) <Serilog.AspNetCore.RequestLoggingMiddleware> HTTP GET /index.html responded 200 in 327.7153 ms {}
2024-06-24 10:05:00 [INF] (0000000013) <Serilog.AspNetCore.RequestLoggingMiddleware> HTTP GET /index.html responded 200 in 334.1519 ms {}
2025-06-24 09:05:00 [INF] (0000000010) <Serilog.AspNetCore.RequestLoggingMiddleware> HTTP GET /index.html responded 200 in 340.1215 ms {}
        """

        self.view.run_command("insert", {"characters": file_content})

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
 
    def test_clear_filters(self):

        self.view.fold(sublime.Region(0, self.view.size()))

        # self.window.run_command('file_filter', {"command_name": "command_clear"})
        self.command.run()

        folded_regions = self.view.folded_regions()

        self.assertEqual(len(folded_regions), 0)
 
    @unittest.skip("Not working")
    def test_clear_highlights(self):

        self.view.add_regions(
            'vsc_file_filter_highlighted_regions'  # Key for the highlighted regions
            , [self.view.line(0)] # List of regions to highlight
            , 'highlight'  # Scope name (use a predefined or custom scope)
            , ''  # No icon
            , sublime.DRAW_NO_FILL
        )

        self.assertEqual(len(self.view.get_regions('vsc_file_filter_highlighted_regions')), 1, "There must be one and only one reagion")

        # self.window.run_command('file_filter', {"command_name": "command_clear"})
        self.command.run()
        
        self.assertEqual(len(self.view.get_regions('vsc_file_filter_highlighted_regions')), 0, "There must be no reagions")