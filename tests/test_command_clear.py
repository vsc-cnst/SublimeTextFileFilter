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
VIEW_SETTINGS_HIGHLIGHTED_REGIONS = file_filter.VIEW_SETTINGS_HIGHLIGHTED_REGIONS

class TestCommandFilter_Clear(TestCase):

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

    def test_UnfoldYes_RmvHighlightsYes_CenterOnCarretYes(self):
        self.run_it(True, True, True)

    def test_UnfoldYes_RmvHighlightsYes_CenterOnCarretNo(self):
        self.run_it(True, True, False)

    def test_UnfoldYes_RmvHighlightsNo_CenterOnCarretYes(self):
        self.run_it(True, False, True)

    def test_UnfoldYes_RmvHighlightsNo_CenterOnCarretNo(self):
        self.run_it(True, False, False)

    def test_UnfoldNo_RmvHighlightsYes_CenterOnCarretYes(self):
        self.run_it(False, True, True)

    def test_UnfoldNo_RmvHighlightsYes_CenterOnCarretNo(self):
        self.run_it(False, True, False)

    def test_UnfoldNo_RmvHighlightsNo_CenterOnCarretYes(self):
        self.run_it(False, False, True)

    def test_UnfoldNo_RmvHighlightsNo_CenterOnCarretNo(self):
        self.run_it(False, False, False)

    def run_it(self, unfold_regions, remove_highlights, center_viewport_on_carret):

        desired_carret_idx = self.view.size();
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(desired_carret_idx))

        command_filter = FileFilter(self.window)
        command_filter.run()
        command_filter.set_regex(r"ApplicableState: 0")
        
        self.assertFalse(self.view.visible_region().contains(desired_carret_idx), "Carret position cannot be visible at test start")

        command_filter.apply()

        initial_highlights_count = len(self.view.get_regions(VIEW_SETTINGS_HIGHLIGHTED_REGIONS))
        self.assertTrue(self.view.visible_region().contains(desired_carret_idx), "Carret position MUST be visible after filter run")
        self.assertFalse(initial_highlights_count == 0, "No highlights at test start")
        
        command_filter.clear(unfold_regions, remove_highlights, center_viewport_on_carret)

        if unfold_regions and center_viewport_on_carret == False:
            self.assertFalse(self.view.visible_region().contains(desired_carret_idx), f"Carret position CAN NOT be visible after run command clear when unfold_regions=='{unfold_regions}'' and center_viewport_on_carret=='{center_viewport_on_carret}'")
        else:
            self.assertTrue(self.view.visible_region().contains(desired_carret_idx), f"Carret position MUST be visible after run command clear when unfold_regions=='{unfold_regions}'' and center_viewport_on_carret=='{center_viewport_on_carret}'")

        highlights_count = len(self.view.get_regions(VIEW_SETTINGS_HIGHLIGHTED_REGIONS))
        if remove_highlights:
            self.assertTrue(highlights_count == 0, "Not all were removed highlights")
        else:
            self.assertTrue(highlights_count == initial_highlights_count, f"Final highlights count({highlights_count}) does not match initial count ({initial_highlights_count})")

