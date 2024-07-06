import sublime
import sublime_plugin
import re
import inspect
import logging

from enum import Enum

import time

class MyEnum(Enum):

    @classmethod
    def all_members(cls):
        return [member for member in cls]

    @classmethod
    def all_values(cls):
        return [member._value_ for member in cls]


class PairEnum(MyEnum):

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

class HighlightTypes(PairEnum):

    # Flags for how to draw the regions
    outline = 'Outline', sublime.DRAW_NO_FILL
    solid = 'Solid', sublime.DRAW_NO_OUTLINE 
    underline_solid = 'Underline solid', sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_stippled = 'Underline stippled', sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    underline_squiggly= 'Underline squiggly', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    none = 'None', sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
   
class ReservedRegexListOptions(PairEnum):

    PROMPT = "prompt", "___prompt___"
    CLEAR = "clear", "___clear___"

class SettingViewConstants(MyEnum):
    

    CURRENT_REGEX = 'vsc_file_filter_CURRENT_REGEX.value'
    CURRENT_FOLDING_TYPE = 'vsc_file_filter_CURRENT_FOLDING_TYPE.value'
    CURRENT_HIGHLIGHT_TYPE = 'vsc_file_filter_CURRENT_HIGHLIGHT_TYPE.value'

    STATUS_BAR_REGEX = 'vsc_file_filter_status_bar_regex'
    HIGHLIGHTED_REGIONS = 'vsc_file_filter_highlighted_regions'



SETTING_OBSERVER_KEY = "cc362837-008e-4a24-8bc2-b32c8d455c21"

SETTING_FILE_SETTINGS_NAME = 'file_filter.sublime-settings'
SETTING_FILE_SETTINGS_PROP_REGEX_LIST = 'regex_list'


LOGGING_LEVEL = logging.DEBUG
LOG_TIME = False


def plugin_loaded() -> None:
    pass
    settings_changed()


def plugin_unloaded() -> None:
    SETTINGS = sublime.load_settings(SETTING_FILE_SETTINGS_NAME)
    SETTINGS.clear_on_change(SETTING_OBSERVER_KEY)


def settings_changed() -> None:
    pass


class FileFilter(sublime_plugin.WindowCommand):

    def __init__(self, window):

        super().__init__(window)
        
        logging.basicConfig(level=LOGGING_LEVEL, format=f"[%(levelname)3s][FileFilter][%(name)s.%(funcName)s():%(lineno)s]  %(message)s")

        self.SETTINGS = sublime.load_settings(SETTING_FILE_SETTINGS_NAME)
        self.SETTINGS.add_on_change(SETTING_OBSERVER_KEY, settings_changed)

        self.REGEX_OPTIONS_LIST = [[m.description, m.value] for m in ReservedRegexListOptions.all_members()] + self.SETTINGS.get(SETTING_FILE_SETTINGS_PROP_REGEX_LIST, [])

        self.regex = None
        self.folding_type = FoldingTypes.line
        self.highlight_type = HighlightTypes.solid

        self.regex_prompt_input_panel = None


    def run(self):
        self.view = self.window.active_view()
        self.log = logging.getLogger(self.__class__.__name__)

        self.regex = self.view.settings().get(SettingViewConstants.CURRENT_REGEX.value, "")
        self.folding_type = FoldingTypes[self.view.settings().get(SettingViewConstants.CURRENT_FOLDING_TYPE.value, FoldingTypes.line.name)]
        self.highlight_type = HighlightTypes[self.view.settings().get(SettingViewConstants.CURRENT_HIGHLIGHT_TYPE.value, HighlightTypes.solid.name)]


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

    def command_prompt_regex(self, regex=None):
        self.log.debug(self.get_state(regex))
    
        def on_input_done(regex):
            self.set_regex(regex)
            self.apply()

        self.regex_prompt_input_panel =  self.window.show_input_panel(
            "Enter regex:"
            , regex or self.regex or ""
            , on_input_done
            , None # self.on_change
            , None  # self.on_cancel
        )


    def command_set_folding_type(self, folding_type):
        self.log.debug(self.get_state(folding_type))

        if not folding_type or folding_type not in [ft for ft in FoldingTypes]:
            self.view.settings().set(SettingViewConstants.CURRENT_FOLDING_TYPE.value, FoldingTypes.line.name)
            return

        self.view.settings().set(SettingViewConstants.CURRENT_FOLDING_TYPE.value, folding_type.name)
        self.folding_type = folding_type
        self.apply()


    def command_set_highlight_type(self, highlight_type):
        self.log.debug(self.get_state(highlight_type))
        
        if not highlight_type or highlight_type not in HighlightTypes.all_members():
            self.view.settings().erase(SettingViewConstants.CURRENT_HIGHLIGHT_TYPE.value)
            return

        self.view.settings().set(SettingViewConstants.CURRENT_HIGHLIGHT_TYPE.value, highlight_type.name)
        self.highlight_type = highlight_type
        self.apply()


    def set_regex(self, regex = ""):
        self.log.debug(self.get_state(regex))

        if not regex:
            self.view.settings().erase(SettingViewConstants.CURRENT_REGEX.value)
            return
        else:
            self.view.settings().set(SettingViewConstants.CURRENT_REGEX.value, regex)
            self.regex = regex

        if hasattr(self, 'input_panel') and self.input_panel is not None:
            self.input_panel.close()


    def apply(self):
        self.log.debug(self.get_state())
        
        if not self.regex:
            return

        self.clear()

        view_size = self.view.size()

        matches_regions = self.view.find_all(self.regex)
        total_matches_regions = len(matches_regions)

        if(total_matches_regions == 0):
            self.view.set_status(key=SettingViewConstants.STATUS_BAR_REGEX.value, value= f"No Matches Regions with /{self.regex})/")

        status = f'Folding {self.folding_type.value}' \
            + f' Highlight: {self.highlight_type.description}' \
            + f' Filter /{self.regex}/' \
            + f' Total Matches {total_matches_regions}'

        self.view.set_status(key=SettingViewConstants.STATUS_BAR_REGEX.value, value=status)

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
                    elif a != b:
                        self.fold_span([middle], remove_last_char=False)


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
                SettingViewConstants.HIGHLIGHTED_REGIONS.value  # Key for the highlighted regions
                , matches_regions  # List of regions to highlight
                , 'highlight'  # Scope name (use a predefined or custom scope)
                , ''  # No icon
                , self.highlight_type.value
            )


    def clear(self):
        self.log.debug(self.get_state())

        self.view.unfold(sublime.Region(0, self.view.size()))
        self.view.erase_regions(SettingViewConstants.HIGHLIGHTED_REGIONS.value)
        self.view.set_status(key=SettingViewConstants.STATUS_BAR_REGEX.value, value="")


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


class FileFilterQuickPanelCommand(FileFilter):

    def run(self):
        super().run()

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

        self.clear()


class FileFilterEditSettingsCommand(FileFilter):

    def run(self):
        super().run()
