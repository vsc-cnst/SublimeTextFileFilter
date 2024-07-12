import sys
import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch

class TestCommandHighlight(TestCase):
        
    def setUp(self): 
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)


    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")
 
    @unittest.skip("test actions after highlight selection")
    def test_highlight(self, highlightTypes):
       pass