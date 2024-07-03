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

import time


DEBUG = False
LOG_TIME = True
    
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
    
    FILTER_ACTIVE = 'vsc_file_filter_is_active'

    CURRENT_REGEX = 'vsc_file_filter_current_regex'
    CURRENT_FOLDING_TYPE = 'vsc_file_filter_current_folding_type'
    CURRENT_HIGHLIGHT_TYPE = 'vsc_file_filter_current_highlight_type'

    STATUS_BAR_REGEX = 'vsc_file_filter_status_bar_regex'
    HIGHLIGHTED_REGIONS = 'vsc_file_filter_highlighted_regions'

class SettingFiles(Enum):

    FILE_NAME_INTERNAL_SETTINGS = 'settings-internal-file-filter.sublime-settings'
    FILE_NAME_EXTERNAL_SETTINGS = 'settings-external-file-filter.sublime-settings'
    
    OPTION_REGEX_LIST = 'regex_list'

class ReservedRegexListOptions(Enum):

    PROMPT = "___prompt___"
    CLEAR = "___clear___"

class FileFilter(sublime_plugin.WindowCommand):

    def __init__(self, window, DEBUG=DEBUG):

        super().__init__(window)

        self.DEBUG = DEBUG;
        
        self.regex = None
        self.folding_type = FoldingTypes.line
        self.highlight_type = HighlightTypes.solid
        
        self.internal_settings = sublime.load_settings(SettingFiles.FILE_NAME_INTERNAL_SETTINGS.value)
        self.external_settings = sublime.load_settings(SettingFiles.FILE_NAME_EXTERNAL_SETTINGS.value)

        self.regex_options_list = ( 
            self.internal_settings.get(SettingFiles.OPTION_REGEX_LIST.value, []) 
            + self.external_settings.get(SettingFiles.OPTION_REGEX_LIST.value, [])
        )   


    def run(self, DEBUG=DEBUG):
        self.view = self.window.active_view()
        self.load_regex_from_settings()
        self.load_folding_type_from_settings()
        self.load_highlight_type_from_settings()


    def command_filter(self, regex):
        self.log_state((regex, ReservedRegexListOptions.PROMPT.value))
        
        if regex == ReservedRegexListOptions.PROMPT.value:

            self.input_panel =  self.window.show_input_panel(
                "Enter  regex:"
                , self.regex or ""
                , self.command_filter
                , None # self.on_change
                , None  # self.on_cancel
            )
            self.input_panel.set_syntax_file("Packages/Text/Plain text.tmLanguage")
            return

        if regex == ReservedRegexListOptions.CLEAR.value:
            self.clear()
            return
        
        self.set_regex(regex)
        self.apply()

    def load_folding_type_from_settings(self):
        self.folding_type = FoldingTypes[self.view.settings().get(SettingView.CURRENT_FOLDING_TYPE.value, FoldingTypes.line.name)]

    def command_set_folding_type(self, folding_type):
        self.log_state(folding_type.value)

        if not folding_type or folding_type not in [ft for ft in FoldingTypes]:
            self.view.settings().set(SettingView.CURRENT_FOLDING_TYPE.value, FoldingTypes.line.name)
            return

        self.view.settings().set(SettingView.CURRENT_FOLDING_TYPE.value, folding_type.name)
        self.folding_type = folding_type
        self.apply()

    def load_highlight_type_from_settings(self):
        self.highlight_type = HighlightTypes[self.view.settings().get(SettingView.CURRENT_HIGHLIGHT_TYPE.value, HighlightTypes.solid.name)]

    def command_set_highlight_type(self, highlight_type):
        self.log_state(highlight_type.value)
        
        if not highlight_type or highlight_type not in [ht for ht in HighlightTypes]:
            self.view.settings().erase(SettingView.CURRENT_HIGHLIGHT_TYPE.value)
            return

        self.view.settings().set(SettingView.CURRENT_HIGHLIGHT_TYPE.value, highlight_type.name)
        self.highlight_type = highlight_type
        self.apply()

    def load_regex_from_settings(self):
        self.regex = self.view.settings().get(SettingView.CURRENT_REGEX.value, "")

    def set_regex(self, regex = ""):
        self.log_state(regex)

        if not regex:
            self.view.settings().erase(SettingView.CURRENT_REGEX.value)
            return
        else:
            self.view.settings().set(SettingView.CURRENT_REGEX.value, regex)
            self.regex = regex

        if hasattr(self, 'input_panel') and self.input_panel is not None:
            self.input_panel.close()

    def apply(self):
        self.log_state()
        
        if not self.regex:
            return

        self.clear()

        start_time = time.time()

        view_size = self.view.size()

        matches_regions = self.view.find_all(self.regex)
        total_matches_regions = len(matches_regions)

        status = {
            'Folding': self.folding_type.value,
            'Highlight': self.highlight_type.description,
            'Filter': "/" + str(self.regex) +"/",
            'Total Matches': total_matches_regions,
        }
        
        self.view.set_status(key=SettingView.STATUS_BAR_REGEX.value, value= str(status))

        if self.folding_type is not FoldingTypes.highlight_only and total_matches_regions > 0:

            self.log_state()

            temp_fold_regions = [sublime.Region(0, 0)] + matches_regions + [sublime.Region(view_size, view_size)]
            fold_regions = [ sublime.Region(prev.end(), curr.begin()) for prev, curr in zip(temp_fold_regions, temp_fold_regions[1:])]
            

            first_fold = fold_regions[0]
            last_fold = fold_regions[-1]
            
            # fold lines with no match
            for fold in fold_regions:

                if fold.size() <= 0 or fold.begin() >= fold.end():
                    continue

                if fold is first_fold or fold is last_fold:
                    self.view.fold(fold)
                    continue

                a = self.view.full_line(fold.begin())
                b = self.view.full_line(fold.end())

                if a == b:
                    self.view.fold(fold)
                    continue

                first = None
                middle = None

                if self.folding_type == FoldingTypes.match_only:
                    first = (fold.begin(), b.begin() - 1) 
                    middle = (0,0)
                else:
                    first = (fold.begin(), a.end()-1)
                    middle = (a.end() , b.begin()) 

                last = (b.begin(), fold.end())

                if  first[0] < first[1] and self.folding_type in [FoldingTypes.match_only, FoldingTypes.after_only]:
                    self.view.fold(sublime.Region(*first))

                if middle[0] < middle[1]:
                    self.view.fold(sublime.Region(*middle))

                if last[0] < last[1] and self.folding_type in [FoldingTypes.match_only, FoldingTypes.before_only]:
                    self.view.fold(sublime.Region(*last))


        if LOG_TIME:
            print("--- %s seconds ---" % (time.time() - start_time))

        if len(matches_regions) > 0 and self.highlight_type != HighlightTypes.none:
            self.view.add_regions(
                SettingView.HIGHLIGHTED_REGIONS.value  # Key for the highlighted regions
                , matches_regions  # List of regions to highlight
                , 'highlight'  # Scope name (use a predefined or custom scope)
                , ''  # No icon
                , self.highlight_type.value
            )

    def apply_old(self):
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

        self.view.settings().set(SettingView.CURRENT_REGEX.value, True)
        
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
        
        if(not self.DEBUG):
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
        
        if(not self.DEBUG):
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


class FileFilterCommand(FileFilter):

    def run(self):
        self.log_state()

        super().run()
    
        self.window.show_quick_panel(
            self.regex_options_list
            , on_select= lambda idx :self.command_filter(None if idx < 0 else self.regex_options_list[idx][1]) 
        )

class FileFilterSetFoldingTypeCommand(FileFilter):

    def run(self):
        self.log_state()

        super().run()
    
        self.window.show_quick_panel(
            [ft.value for ft in FoldingTypes]
            , on_select = lambda idx : self.command_set_folding_type(self.folding_type if idx < 0 else [ft for ft in FoldingTypes][idx])
        )

class FileFilterSetHighlightTypeCommand(FileFilter):

    def run(self):
        self.log_state()
        
        super().run()
    
        self.window.show_quick_panel(
            [ht.description for ht in HighlightTypes]
            , on_select = lambda idx : self.command_set_highlight_type(self.highlight_type if idx < 0 else [ft for ft in HighlightTypes][idx])
        )

class FileFilterClearCommand(FileFilter):

    def run(self):
        self.log_state()
        
        super().run()
    
        self.clear()
