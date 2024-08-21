import sys
import os

import sublime
import sublime_plugin
import unittest
from unittest import TestCase
from unittest.mock import patch

file_filter = sys.modules["File Filter.file_filter"]

FileFilter = file_filter.FileFilter

FoldingTypes = file_filter.FoldingTypes
HighlightTypes = file_filter.HighlightTypes

class TestCommandFilter(TestCase):

    @classmethod
    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.window.focus_view(self.view)



        self.view.run_command("insert", {"characters": self.file})
        self.vie_size = self.view.size()

        self.regex = r"[0-9]"
        self.lines = self.view.lines(sublime.Region(0,self.vie_size))

        self.command = FileFilter(self.window)
        self.command.run()
        self.command.set_regex(self.regex)
  
    @classmethod
    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.window.focus_view(self.view)
            self.view.window().run_command("close_file")

class TestCommandFilter_File1(TestCommandFilter):     

    @classmethod
    def setUpClass(self):
        current_package_path = os.path.dirname(__file__)
        self.file = open(os.path.join(current_package_path, 'fixtures', "example_text_case_1.txt")).read()


    def test_initial_state(self):

        self.assertIsNot(self.command.REGEX_OPTIONS_LIST, None)

        self.assertEqual(self.command.folding_type, FoldingTypes.line)
        self.assertEqual(self.command.highlight_type, HighlightTypes.solid)


    def test_line(self):

        self.command.command_set_folding_type(FoldingTypes.line)
        self.assertEqual(self.command.folding_type, FoldingTypes.line)
        
        self.folded_regions = self.view.folded_regions()

        self.assertEqual(len(self.folded_regions), 3)

        expected_values = [(0, 3), (7, 11), (15, 19)]
        actual_values = [ r.to_tuple() for r in self.view.folded_regions()]
        
        self.assertEqual(actual_values, expected_values)


    def test_match_only(self):

        self.command.command_set_folding_type(FoldingTypes.match_only)
        self.assertEqual(self.command.folding_type, FoldingTypes.match_only)
        
        self.folded_regions = self.view.folded_regions()

        expected_values = [(0, 3), (4, 5), (6, 11), (12, 13), (14, 19), (20, 21), (22, 23), (24, 25)]
        actual_values = [ r.to_tuple() for r in self.view.folded_regions()]
        
        self.assertEqual(actual_values, expected_values)

    def test_fold_before(self):

        self.command.command_set_folding_type(FoldingTypes.before_only)
        self.assertEqual(self.command.folding_type, FoldingTypes.before_only)
        
        self.folded_regions = self.view.folded_regions()

        expected_values = [(0, 5), (8, 13), (16, 21)]
        actual_values = [ r.to_tuple() for r in self.view.folded_regions()]
        
        self.assertEqual(actual_values, expected_values)


    def test_fold_after(self):

        self.command.command_set_folding_type(FoldingTypes.after_only)
        self.assertEqual(self.command.folding_type, FoldingTypes.after_only)
        
        expected_values = [(0, 3) , (6, 11), (14, 19), (24, 25)]
        actual_values = [ r.to_tuple() for r in self.view.folded_regions()]

        self.assertEqual(actual_values, expected_values)


class TestCommandFilter_File2(TestCommandFilter):


    @classmethod
    def setUpClass(self):
        current_package_path = os.path.dirname(__file__)
        self.file = open(os.path.join(current_package_path, 'fixtures', "example_text_case_2.txt")).read()


    def test_line(self):

        self.command.command_set_folding_type(FoldingTypes.line)
        self.assertEqual(self.command.folding_type, FoldingTypes.line)
        
        self.folded_regions = self.view.folded_regions()

        expected_values = [(0, 7), (11, 15), (19, 23), (30, 34)]
        actual_values = [ r.to_tuple() for r in self.view.folded_regions()]
        
        self.assertEqual(actual_values, expected_values)


class TestCommandFilter_GoToCarretOnClear(TestCommandFilter):


    @classmethod
    def setUpClass(self):
        current_package_path = os.path.dirname(__file__)
        self.file = open(os.path.join(current_package_path, 'fixtures', "log-example.log")).read()


    def test_goToCarretOnClear(self):

        desired_carret_idx = self.view.size();

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(desired_carret_idx))

        self.assertFalse(self.view.visible_region().contains(desired_carret_idx), "Carret position cannot be visible at test start")

        self.view.window().run_command("file_filter_clear")

        self.assertTrue(self.view.visible_region().contains(desired_carret_idx), "Carret position must be visible after command run clear")
 
