import sys
import os
pkg_folder = os.path.dirname(__file__)
enum_folder = os.path.join(pkg_folder, "enum")


if pkg_folder not in sys.path:
    sys.path.append(pkg_folder)

import sublime
import sublime_plugin
import re
import inspect

from enum import Enum
    
class FoldingTypes(Enum):

    line = 'Line'
    match_only = 'Match only'
    before_only = 'Fold content before only'
    after_only = 'Fold content after only'
    highlight_only = 'Highlight only'

class HighlightTypes(Enum):

    # Flags for how to draw the regions
    outline = 'Outline', sublime.DRAW_NO_FILL
    solid = 'Solid', sublime.DRAW_NO_OUTLINE 
    underline_solid = 'Underline solid', sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_stippled = 'Underline stippled', sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_squiggly= 'Underline squiggly', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    none = 'None', sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE

    def __new__(cls, desc, value):
        obj = object.__new__(cls)

        obj._value_ = value
        obj.description = desc

        return obj
   
class SettingView(Enum):
    
    CURRENT_REGEX = 'vsc_file_filter_current_regex'
    STATUS_BAR_REGEX = 'vsc_file_filter_status_bar_regex'
    HIGHLIGHTED_REGIONS = 'logs_file_lines_highlights'

class SettingFiles(Enum):

    FILE_NAME_INTERNAL_SETTINGS = 'settings-internal-file-filter.sublime-settings'
    FILE_NAME_EXTERNAL_SETTINGS = 'settings-internal-file-filter.sublime-settings'
    
    OPTION_REGEX_LIST = 'regex_list'

class ReservedRegexListOptions(Enum):

    PROMPT = "___prompt___"
    CLEAR = "___clear___"

class FileFilterCommand(sublime_plugin.WindowCommand):

    def __init__(self, window):

        super().__init__(window)

        self.regex = None
        self.folding_type = FoldingTypes.line
        self.highlight_type = HighlightTypes.solid


    def run(self, command_name="command_filter"):
        self.log_state(command_name)
        
        self.view = self.window.active_view()
        self.FILE_NAME_INTERNAL_SETTINGS = sublime.load_settings(SettingFiles.FILE_NAME_INTERNAL_SETTINGS.value)
        self.FILE_NAME_EXTERNAL_SETTINGS = sublime.load_settings(SettingFiles.FILE_NAME_EXTERNAL_SETTINGS.value)

        self.regex_options_list = ( self.FILE_NAME_INTERNAL_SETTINGS.get(SettingFiles.OPTION_REGEX_LIST.value, []) 
                                        + self.FILE_NAME_EXTERNAL_SETTINGS.get(SettingFiles.OPTION_REGEX_LIST.value, [])
                                )   


        if command_name == "command_filter":
            self.input_quick_panel = self.window.show_quick_panel(
                self.regex_options_list
                , on_select= lambda idx :self.command_filter(None if idx < 0 else self.regex_options_list[idx][1]) 
            )
            return

        if command_name == "command_set_folding_type":
            self.input_quick_panel = self.window.show_quick_panel(
                [ft.value for ft in FoldingTypes]
                , on_select = lambda idx : self.command_set_folding_type(self.folding_type if idx < 0 else [ft for ft in FoldingTypes][idx])
            )
            return

        if command_name == "command_set_highlight_type":
            self.input_quick_panel = self.window.show_quick_panel(
                [ht.description for ht in HighlightTypes]
                , on_select = lambda idx : self.command_set_highlight_type(self.highlight_type if idx < 0 else [ft for ft in HighlightTypes][idx])
            )
            return

        if command_name == "command_clear":
            self.clear()
            return

    def command_filter(self, regex):
        self.log_state((regex, ReservedRegexListOptions.PROMPT.value))

        if regex == ReservedRegexListOptions.PROMPT.value:
            self.input_panel =  self.window.show_input_panel(
                "Enter  regex:"
                , self.regex or ""
                , self.set_regex
                , None #self.on_change
                , None #self.on_cancel
            )
            self.input_panel.set_syntax_file("Packages/Text/Plain text.tmLanguage")
            return

        if regex == ReservedRegexListOptions.CLEAR.value:
            self.clear()
            return
        
        self.set_regex(regex)

    def command_set_folding_type(self, folding_type):
        self.log_state(folding_type.value)

        if not folding_type:
            return
        if folding_type not in [ft for ft in FoldingTypes]:
            return

        self.folding_type = folding_type
        self.apply()

    def command_set_highlight_type(self, highlight_type):
        self.log_state(highlight_type.value)
        
        if not highlight_type:
            return
        if highlight_type not in [ht for ht in HighlightTypes]:
            return

        self.highlight_type = highlight_type
        self.apply()

    def set_regex(self, regex = ""):
        self.log_state(regex)

        if not regex:
            self.view.settings().erase(SettingView.CURRENT_REGEX.value)
            self.clear()
            return
        else:
            self.view.settings().set(SettingView.CURRENT_REGEX.value, regex)
            self.regex = regex

        if hasattr(self, 'input_panel') and self.input_panel is not None:
            self.input_panel.close()

        self.apply()

    def apply(self):
        self.log_state()
        
        #algorithm explained example
        # lines_with_match = [(0,0),(2,4),(8,10)]
        #
        # for previous, current in zip(li, li[1:]):
        #     print(previous[1], current[0])
        #   
        # >>>> output - space between lines
        # >> 0 2
        # >> 4 8    
        
        if not self.regex:
            return

        self.clear()
        self.view.set_status(key=SettingView.STATUS_BAR_REGEX.value, value="Filter: /" + self.regex +"/")

        view_size = self.view.size()

        matches_regions = self.view.find_all(self.regex)
        match_lines = [self.view.lines(r) for r in matches_regions]
        matches_regions_full = [sublime.Region(lines[0].begin(), view_size if  lines[-1].end() == view_size else lines[-1].end() + 1) for lines in match_lines]
        
        # add file begin and file end
        _matches_regions_full = [sublime.Region(0, 0)] + matches_regions_full + [sublime.Region(view_size, view_size)]
    
        # fold lines with no match
        for fold in [sublime.Region(prev.end(), curr.begin()) for prev, curr in zip(_matches_regions_full,_matches_regions_full[1:])]:
            self.view.fold(fold)

        if len(matches_regions) > 0:

            ft = self.folding_type
            for outter_region, inner_region in zip(matches_regions_full, matches_regions):

                if ft == FoldingTypes.match_only or ft == FoldingTypes.before_only:
                    self.view.fold(sublime.Region(outter_region.begin(), inner_region.begin()))

                if  ft == FoldingTypes.match_only or ft == FoldingTypes.after_only:
                    self.view.fold(sublime.Region(inner_region.end(), outter_region.end() - 1))
    
            if self.highlight_type != HighlightTypes.none:
                self.view.add_regions(
                    SettingView.HIGHLIGHTED_REGIONS.value  # Key for the highlighted regions
                    , matches_regions  # List of regions to highlight
                    , 'highlight'  # Scope name (use a predefined or custom scope)
                    , ''  # No icon
                    , self.highlight_type.value
                )

    def clear(self):
        self.log_state()

        self.view.unfold(sublime.Region(0, self.view.size()))
        self.view.erase_regions(SettingView.HIGHLIGHTED_REGIONS.value)
        self.view.set_status(key=SettingView.STATUS_BAR_REGEX.value, value="")

    def log(self, message):
        return
        # Get the current frame
        frame = inspect.currentframe()
        # Get the caller's frame
        caller_frame = frame.f_back
        # Get the caller's function name
        caller_name = caller_frame.f_code.co_name
        # Log the message with the caller's function name
        print('[FileFilterCommand][' + caller_name +']', message)

    def log_state(self, args = None):
        return
        # Get the current frame
        frame = inspect.currentframe()
        # Get the caller's frame
        caller_frame = frame.f_back
        # Get the caller's function name
        caller_name = caller_frame.f_code.co_name
        # Log the message with the caller's function name

        dic = {
            'args': str(args),
            'regex': self.regex,
            'folding_type': self.folding_type.value,
            'highlight_type': self.highlight_type.description,
        }

        exp = '\n\t'.join([ key + ': ' + str(value) for key, value in dic.items()])
        print('[FileFilterCommand][' + caller_name +']', exp)
