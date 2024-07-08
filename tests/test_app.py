import sys
import sublime
import sublime_plugin
import unittest
from unittest import TestCase
import logging

file_filter = sys.modules["File Filter.file_filter"]

LOGGING_LEVEL = file_filter.LOGGING_LEVEL

class TestCommandPrompt(TestCase):
        
    def setUp(self): 
        pass
        # self.window = sublime.active_window()
        # self.view = self.window.new_file()
        # self.window.focus_view(self.view)


    def tearDown(self):
        pass
        # if self.view:
        #     self.view.set_scratch(True)
        #     self.window.focus_view(self.view)
        #     self.view.window().run_command("close_file")
 

    def test_logging_level(self):
        
        self.assertEqual(LOGGING_LEVEL, logging.ERROR, "Loggin Level must be ERROR")

        existing_loggers = logging.root.manager.loggerDict

        self.assertEqual(len(existing_loggers), 9)

        arr = [logging.getLogger(name).level for name in existing_loggers if name.startswith("FileFilter")] 

        self.assertEqual(arr, 7 * [logging.ERROR]) # all loggers have logging level ERROR

        # arr_names = [logging.getLogger(name).name for name in existing_loggers] 
        # self.assertEqual(arr_names,[]) # has 6 loggers
        