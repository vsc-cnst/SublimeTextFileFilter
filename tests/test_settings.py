import sys
import os

import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
import itertools
import json

file_filter = sys.modules["File Filter.file_filter"]
FileFilter = file_filter.FileFilter

class TestSettings(TestCase):

    @classmethod  
    def setUpClass(self):

        package_dir_path = os.path.dirname(os.path.dirname(__file__))
        tests_dir_path = os.path.dirname(__file__)

        self.file = open(os.path.join(tests_dir_path, 'fixtures', "windows.example.log")).read()

    @classmethod
    def setUp(self):
        
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)

        self.view.run_command("insert", {"characters": self.file})
        self.vie_size = self.view.size()


    @classmethod
    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

    @unittest.skip("test default settings combinations")
    def test_settings_default(self):
        pass
        
    @unittest.skip("test different settings combinations")
    def test_settings(self):
        pass
