import sys
import re

import logging
import sublime
import sublime_plugin

from enum import Enum

class MyEnum(Enum):

    @classmethod
    def all_members(cls):
        return [member for member in cls]

    @classmethod
    def all_values(cls):
        return [member._value_ for member in cls]

class TupleEnum(MyEnum):

    def __new__(cls, description, value):
        obj = object.__new__(cls)

        obj._value_ = value
        obj.description = description

        return obj

    @classmethod
    def all_values(cls):
        return [member.value for member in cls]

    @classmethod
    def all_descriptions(cls):
        return [member.description for member in cls]


class FoldingTypes(MyEnum):

    line = 'Line'
    match_only = 'Match only'
    before_only = 'Fold before'
    after_only = 'Fold after'
    highlight_only = 'Highlight only'

class HighlightTypes(TupleEnum):

    # Flags for how to draw the regions
    outline = 'Outline', sublime.DRAW_NO_FILL
    solid = 'Solid', sublime.DRAW_NO_OUTLINE 
    underline_solid = 'Underline solid', sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_stippled = 'Underline stippled', sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_squiggly= 'Underline squiggly', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    none = 'None', sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
   
class ReservedRegexListOptions(TupleEnum):

    PROMPT = "prompt", "___prompt___"
    CLEAR = "clear", "___clear___"



##
## LOGGING  
##

# setting logging
LOGGING_LEVEL = logging.ERROR
# LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = f"[%(levelname)3s][%(name)s.%(funcName)s():%(lineno)s]  %(message)s" 

LOGGER = logging.getLogger('FileFilter')
LOGGER.setLevel(LOGGING_LEVEL)

if not LOGGER.handlers:
    STREAM_HANDLER = logging.StreamHandler()
    _formatter = logging.Formatter(LOGGING_FORMAT)
    STREAM_HANDLER.setFormatter(_formatter)
    LOGGER.addHandler(STREAM_HANDLER)

##
## SETTINGS  
##

# setting file
SETTING_FILE_SETTINGS_NAME = 'file_filter.sublime-settings'
SETTING_FILE_SETTINGS_PROP_REGEX_LIST = 'regex_list'

    
# keys for view.settings 
VIEW_SETTINGS_IS_FILTER_ACTIVE = 'file_filter.view_settings.is_filter_active'
VIEW_SETTINGS_CURRENT_REGEX = 'file_filter.view_settings.current_regex'
VIEW_SETTINGS_CURRENT_FOLDING_TYPE = 'file_filter.view_settings.current_folding_type'
VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE = 'file_filter.view_settings.current_highlight_type'


VIEW_SETTINGS_STATUS_BAR_REGEX = 'file_filter.view_settings.status_bar_regex'
VIEW_SETTINGS_HIGHLIGHTED_REGIONS = 'file_filter.view_settings.highlighted_regions'
    
KEY_MAP_CONTEXT_KEY_CLEAR = "file_filter.keymaps_context.clear"

SETTING_OBSERVER_KEY = "cc362837-008e-4a24-8bc2-b32c8d455c21"
SETTINGS = None



##
## PLUGIN
##

def plugin_loaded() -> None:
    global SETTINGS
    SETTINGS = sublime.load_settings(SETTING_FILE_SETTINGS_NAME)
    SETTINGS.add_on_change(SETTING_OBSERVER_KEY, settings_changed)

    LOGGER.info(f"plugin loaded with settings {SETTINGS}")

def plugin_unloaded() -> None:

    if STREAM_HANDLER:
        STREAM_HANDLER.close()

    LOGGER.info("plugin unloaded")
    SETTINGS = sublime.load_settings(SETTING_FILE_SETTINGS_NAME)
    SETTINGS.clear_on_change(SETTING_OBSERVER_KEY)


def settings_changed() -> None:
    SETTINGS = sublime.load_settings(SETTING_FILE_SETTINGS_NAME)
    LOGGER.info(f"settings reloaded {SETTINGS}")


class FileFilter(sublime_plugin.WindowCommand):

    def __init__(self, window):

        super().__init__(window)
        
        self.log = logging.getLogger(f"FileFilter.{self.__class__.__name__}")

        self.log.setLevel(LOGGING_LEVEL)
        if not LOGGER.handlers:
            self.log.addHandler(STREAM_HANDLER)
        
        self.regex = None
        self.folding_type = FoldingTypes.line
        self.highlight_type = HighlightTypes.solid

        self.regex_prompt_input_panel = None
        
        SETTINGS.add_on_change(SETTING_OBSERVER_KEY, self.on_settings_change)
        self.on_settings_change()

        self.log.info("Command Has Started")


    def run(self):
        self.log.info("entered")

        self.view = self.window.active_view()

        view_settings = self.view.settings()
        self.regex = view_settings.get(VIEW_SETTINGS_CURRENT_REGEX, "")
        self.folding_type = FoldingTypes[view_settings.get(VIEW_SETTINGS_CURRENT_FOLDING_TYPE, FoldingTypes.line.name)]
        self.highlight_type = HighlightTypes[view_settings.get(VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, HighlightTypes.solid.name)]


    def command_prompt_regex(self, regex=None):
        self.log.debug(self.get_state(regex))
    
        def on_input_done(regex):
            self.set_regex(regex)
            self.apply()

        self.regex_prompt_input_panel =  self.window.show_input_panel(
            "Enter regex:"
            , regex or self.regex or ""
            , on_input_done # on_done
            , None # on_change
            , None  # on_cancel
        )

    def command_quick_panel(self, regex):
        self.log.debug(self.get_state(regex))
        
        if regex == ReservedRegexListOptions.CLEAR.value:
            self.clear()
            return
        
        if regex == ReservedRegexListOptions.PROMPT.value:
            self.command_prompt_regex()
            return

        self.command_prompt_regex(regex)
        self.set_regex(regex)
        self.apply()

    def command_set_folding_type(self, folding_type):
        self.log.debug(self.get_state(folding_type))

        if not folding_type or folding_type not in [ft for ft in FoldingTypes]:
            self.view.settings().set(VIEW_SETTINGS_CURRENT_FOLDING_TYPE, FoldingTypes.line.name)
            return

        self.view.settings().set(VIEW_SETTINGS_CURRENT_FOLDING_TYPE, folding_type.name)
        self.folding_type = folding_type
        self.apply()

    def command_set_highlight_type(self, highlight_type):
        self.log.debug(self.get_state(highlight_type))
        
        if not highlight_type or highlight_type not in HighlightTypes.all_members():
            self.view.settings().erase(VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE)
            return

        self.view.settings().set(VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, highlight_type.name)
        self.highlight_type = highlight_type
        self.apply()

    def set_regex(self, regex = ""):
        self.log.debug(self.get_state(regex))

        if not regex:
            self.view.settings().erase(VIEW_SETTINGS_CURRENT_REGEX)
            return
        else:
            self.view.settings().set(VIEW_SETTINGS_CURRENT_REGEX, regex)
            self.regex = regex

        if hasattr(self, 'input_panel') and self.input_panel is not None:
            self.input_panel.close()


    def apply(self):
        self.log.debug(self.get_state())
        
        if not self.regex:
            return

        self.clear()

        self.view.settings().set(VIEW_SETTINGS_IS_FILTER_ACTIVE, True)

        view_size = self.view.size()

        matches_regions = self.view.find_all(self.regex)
        total_matches_regions = len(matches_regions)

        if(total_matches_regions == 0):
            self.view.set_status(key=VIEW_SETTINGS_STATUS_BAR_REGEX, value= f"No Matches Regions with /{self.regex})/")

        status = f'Folding {self.folding_type.value}' \
            + f' Highlight: {self.highlight_type.description}' \
            + f' Filter /{self.regex}/' \
            + f' Total Matches {total_matches_regions}'

        self.view.set_status(key=VIEW_SETTINGS_STATUS_BAR_REGEX, value=status)

        if self.folding_type is not FoldingTypes.highlight_only and total_matches_regions > 0:

            temp_fold_regions = [sublime.Region(0, 0)] + matches_regions + [sublime.Region(view_size, view_size)]
            fold_regions = [ sublime.Region(prev.end(), curr.begin()) for prev, curr in zip(temp_fold_regions, temp_fold_regions[1:])]
            
            first_fold = fold_regions[0]
            last_fold = fold_regions[-1]
            
            self.log.debug(fold_regions)

            # fold lines with no match
            for fold in fold_regions:

                self.log.debug(f'.current fold: {fold}.')
                if fold == first_fold :
                    self.log.debug(f'is first fold')
                if fold == last_fold :
                    self.log.debug(f'is last fold')

                if fold.size() <= 0 or fold.begin() >= fold.end():
                    self.log.debug(f'Invalidfold size. continue..')
                    continue

                a = self.view.full_line(fold.begin())
                b = self.view.full_line(fold.end())

                self.log.debug(f'line a: {a}, line b:{b}')

                if a == b:
                    self.log.debug(f'a == b. same line')
                    first = sublime.Region(fold.begin(), fold.begin())
                    middle = fold
                    last = sublime.Region(fold.end(),fold.end()) 
                else:
                    first = sublime.Region(fold.begin(), a.end())
                    middle = sublime.Region(a.end(),b.begin())
                    last = sublime.Region(b.begin(),fold.end())  

                self.log.debug(f'first {first}, middle {middle}, last {last}')

                if self.folding_type == FoldingTypes.match_only:

                    if fold is first_fold:
                        self.fold_span([first, middle], remove_last_char=True)
                        self.fold_span(last)
                    elif a == b:
                        self.fold_span([middle], remove_last_char=False)
                    else:
                        self.fold_span([first,middle], remove_last_char=True)
                        self.fold_span(last)

                elif self.folding_type is FoldingTypes.line:

                    if fold is first_fold:
                        self.fold_span([first, middle], remove_last_char=True)
                    if fold is last_fold and a!=b:
                        self.fold_span([middle, last])
                    elif a != b:
                        middle.a = middle.a - 1
                        self.fold_span([middle], remove_last_char=True)


                elif self.folding_type is FoldingTypes.before_only:

                    if fold is first_fold:
                        self.fold_span([first, last], remove_last_char=False)
                    elif a != b:
                        self.fold_span([middle, last], remove_last_char=False)
                    else:
                        self.fold_span([last], remove_last_char=False)

                elif self.folding_type is FoldingTypes.after_only:

                    if fold is last_fold:
                        self.fold_span(fold)
                    else:
                        self.fold_span([first, middle], remove_last_char=True)

        if self.highlight_type is not HighlightTypes.none:
            self.view.add_regions(
                VIEW_SETTINGS_HIGHLIGHTED_REGIONS  # Key for the highlighted regions
                , matches_regions  # List of regions to highlight
                , 'highlight'  # Scope name (use a predefined or custom scope)
                , ''  # No icon
                , self.highlight_type.value
            )


    def clear(self):
        self.log.debug(self.get_state())

        self.view.unfold(sublime.Region(0, self.view.size()))
        self.view.erase_regions(VIEW_SETTINGS_HIGHLIGHTED_REGIONS)
        self.view.set_status(key=VIEW_SETTINGS_STATUS_BAR_REGEX, value="")


    def fold_span(self, source, remove_last_char=False):
        
        if type(source) is list:
            a = min([ r.a for r in source])
            b = max([ r.b for r in source]) - (1 if remove_last_char else 0)
        else:
            a = source.a
            b = source.b - (1 if remove_last_char else 0)

        if b <= a:
            self.log.debug(f"from {source} NOT folding {(a, b)}, remove_last_char: {remove_last_char}")
            return False
        
        self.log.debug(f"from {source} folding {(a, b)}, remove_last_char: {remove_last_char}")

        return self.view.fold(sublime.Region(a, b))


    def get_state(self, args=None):
        pad = 0
        regex = '\"\"' if self.regex is not None and len(self.regex) == 0 else self.regex
        return f'args: {str(args):^{pad}},  folding_type: {self.folding_type.value:^{pad}}, highlight_type: {self.highlight_type.description:^{pad}}, regex: {regex:^{pad}}'


    def on_settings_change(self):
        self.log.debug(f"Settings changed")
        
        self.REGEX_OPTIONS_LIST = [[r.description, r.value] for r in ReservedRegexListOptions.all_members()] + SETTINGS.get(SETTING_FILE_SETTINGS_PROP_REGEX_LIST, [])
        self.log.debug(f"Settings changed {self.REGEX_OPTIONS_LIST}")
        

class FileFilterQuickPanelCommand(FileFilter):

    def run(self):
        super().run()
        self.log.debug(self.REGEX_OPTIONS_LIST)

        self.window.show_quick_panel(
            self.REGEX_OPTIONS_LIST
            , on_select= lambda idx :self.command_quick_panel(None if idx < 0 else self.REGEX_OPTIONS_LIST[idx][1]) 
        )


class FileFilterPromptRegexCommand(FileFilter):

    def run(self):
        super().run()

        self.command_prompt_regex()


class FileFilterSetFoldingTypeCommand(FileFilter):

    def run(self):
        super().run()
    
        self.window.show_quick_panel(
            FoldingTypes.all_values()
            , on_select = lambda idx : self.command_set_folding_type(self.folding_type if idx < 0 else FoldingTypes.all_members()[idx])
        )


class FileFilterSetHighlightTypeCommand(FileFilter):

    def run(self):
        super().run()
        
        self.window.show_quick_panel(
            HighlightTypes.all_descriptions()
            , on_select = lambda idx : self.command_set_highlight_type(self.highlight_type if idx < 0 else HighlightTypes.all_members()[idx])
        )


class FileFilterClearCommand(FileFilter):

    def run(self):
        super().run()

        self.view.settings().erase(VIEW_SETTINGS_IS_FILTER_ACTIVE)
        self.clear()


class FileFilterListener(sublime_plugin.EventListener):

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == KEY_MAP_CONTEXT_KEY_CLEAR:
            is_file_filter_active = view.settings().get(VIEW_SETTINGS_IS_FILTER_ACTIVE, False)
            LOGGER.debug(f"key: '{KEY_MAP_CONTEXT_KEY_CLEAR}, returning '{VIEW_SETTINGS_IS_FILTER_ACTIVE} -> {is_file_filter_active }")
            return is_file_filter_active
        return None