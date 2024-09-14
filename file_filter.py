import logging
import sublime_plugin # type: ignore

from .utils import commands_override

from .utils.logging import CustomLogger
from .utils.enums import FoldingTypes, HighlightTypes
from .utils.view  import VIEW_SETTINGS_CURRENT_REGEX, VIEW_SETTINGS_REGEX_HISTORY, VIEW_SETTINGS_IS_FILTER_ACTIVE
from .utils import view as view_utils
from .utils import mini_html

    
##
##
## SETTINGS
##
##

SETTING_FILE_SETTINGS_NAME = 'file_filter.sublime-settings'

KEY_MAP_CONTEXT_KEY_CLEAR = "file_filter.keymaps_context.clear"

##
##
## LOGGING  
##
##

logging.setLoggerClass(CustomLogger)
LOGGER = logging.getLogger('FileFilter')


##
##
## PLUGIN
##
##


def plugin_loaded() -> None:
    LOGGER.info(f"plugin loaded")

def plugin_unloaded() -> None:
    LOGGER.info("plugin unloaded")


##
##
## File Filter Command
##
##

class FileFilterCommand(commands_override.TextCommand):

    def __init__(self, view):
        super().__init__(view, SETTING_FILE_SETTINGS_NAME)

    def run(self, edit, option=None, history=None, regex=None):
        self.logger.debug(option, regex)

    def input(self, args):
        self.logger.debug(args)
        return OptionsInputHandler(self.view, self.settings_file, self.logger)

class OptionsInputHandler(commands_override.ListInputHandler):

    def name(self):
        self.logger.debug('')
        return "option"

    def list_items(self):
        self.logger.debug('')
        return [
            ("New", "new"),
            ("New from selection", "selection"),
            ("From history", "history"),
            ("From favorites", "favorites"),
            ("Clear", "clear")
        ]

    def next_input(self, args):
        self.logger.debug(args)
        selected_option = args.get('option')

        if selected_option == "new":
            return RegexInputHandler(self.view, self.settings_file, self.logger)
        if selected_option == "history":
            return HistoryInputHandler(self.view, self.settings_file, self.logger)
        if selected_option == "selection":
            return RegexInputHandler(self.view, self.settings_file, self.logger, "selected text")
        if selected_option == "favorites":
            return FavoritsInputHandler(self.view, self.settings_file, self.logger)
        if selected_option == "clear":
            clear_settings = self.settings.get('on_clear_command_options', {})
            view_utils.clear(
                self.logger,
                self.view,
                unfold_regions = clear_settings.get('unfold_regions', True),
                remove_highlights = clear_settings.get('remove_highlights', True),
                center_viewport_on_carret = clear_settings.get('center_viewport_on_carret', True),
            )
        return None

class HistoryInputHandler(commands_override.ListInputHandler):

    def __init__(self, view, settings_file, logger):
        super().__init__(view, settings_file, logger)

        self.history = view.settings().get(VIEW_SETTINGS_REGEX_HISTORY, [])

    def name(self):
        return "history"

    def list_items(self):
        iist_items = self.view.settings().get(VIEW_SETTINGS_REGEX_HISTORY, [])
        iist_items = iist_items if bool(iist_items) else ['** empty history **']
        self.logger.debug(iist_items=iist_items)
        return iist_items

    def preview(self, value):
        self.logger.debug(value)
        if len(value) == 0 :
            return
        # return f"Total matches: {len(self.view.find_all(value))} \n for regex: /{value}/{self.global_regex_flags}"
        return mini_html.create_preview(
            ("Total matches",len(self.view.find_all(value))),
            [
                ('Folding:', view_utils.get_folding_type(self.logger, self.view, self.settings).value),
                ('Highlight:',view_utils.get_highlight_type(self.logger, self.view, self.settings).description)
            ]
        )
        

    def confirm(self, text):
        self.logger.debug(text)

        view_utils.add_to_history(self.logger, self.view, text)

        view_utils.filter(self.logger, self.view, text, view_utils.get_folding_type(self.logger, self.view, self.settings), view_utils.get_highlight_type(self.logger, self.view, self.settings))

        
class FavoritsInputHandler(commands_override.ListInputHandler):
    
    def name(self):
        return "favorites"

    def list_items(self):
        favorits = self.settings.get('favorits', [])
        return [(f.get('name', ""), f.get('expression', "")) for f in favorits]

    def confirm(self, text):
        self.logger.debug(text)

        view_utils.add_to_history(self.logger, self.view, text)

        view_utils.filter(self.logger, self.view, text, view_utils.get_folding_type(self.logger, self.view, self.settings), view_utils.get_highlight_type(self.logger, self.view, self.settings))


class RegexInputHandler(commands_override.TextInputHandler):

    def __init__(self, view, settings_file, logger, filter=None):
        super().__init__(view, settings_file, logger)
       
        self.global_regex_flags = self.settings.get('global_regex_flags', "")
        self.filter = filter or view.settings().get(VIEW_SETTINGS_CURRENT_REGEX, None)
        self.history = view.settings().get(VIEW_SETTINGS_REGEX_HISTORY, [])

        self.logger.debug(self.filter, self.global_regex_flags)
        
    
    def name(self):
        return "regex"

    def initial_selection(self):
        return None

    def initial_text(self):
        self.logger.debug(self.filter)
        return self.filter or ""

    def placeholder(self):
        self.logger.debug(filter=self.filter)
        return None if not self.filter else "Enter your regex here"

    def validate(self, text):
        self.logger.debug(text)
        return len(text) > 0

    def preview(self, value):
        self.logger.debug(value)
        if len(value) == 0 :
            return

        return mini_html.create_preview(
            ("Total matches",len(self.view.find_all(value))),
            [
                ('Folding:', view_utils.get_folding_type(self.logger, self.view, self.settings).value),
                ('Highlight:',view_utils.get_highlight_type(self.logger, self.view, self.settings).description)
            ]
        )


    def confirm(self, text):
        self.logger.debug(text)

        view_utils.add_to_history(self.logger, self.view, text)
        
        view_utils.filter(self.logger, self.view, text, view_utils.get_folding_type(self.logger, self.view, self.settings), view_utils.get_highlight_type(self.logger, self.view, self.settings))

    def next_input(self, args):
        self.logger.debug(args)
        return None


##
##
## Set Folding Type Command
##
##

class SetFoldingTypeCommand(commands_override.TextCommand):

    def __init__(self, view):
        super().__init__(view, SETTING_FILE_SETTINGS_NAME)

    def run(self, edit, folding_types=None):
        self.logger.debug(folding_types=folding_types)


    def input(self, args):
        self.logger.debug(args)
        return FoldingTypesInputHandler(self.view, self.settings_file, self.logger)

class FoldingTypesInputHandler(commands_override.ListInputHandler):

    def name(self):
        return "folding_types"

    def list_items(self):
        return [(ft.value, ft.name) for ft in FoldingTypes.all_members()]


    def confirm(self, folding_type):
        self.logger.debug(folding_type=folding_type)
        view_utils.set_folding_type(self.logger, self.view, self.settings, folding_type)
        view_utils.filter(self.logger, self.view, view_utils.get_current_regex(self.logger, self.view, self.settings), view_utils.get_folding_type(self.logger, self.view, self.settings), view_utils.get_highlight_type(self.logger, self.view, self.settings))


##
##
## Set Folding Highlight Command
##
##

class SetHighlightTypeCommand(commands_override.TextCommand):

    def __init__(self, view):
        super().__init__(view, SETTING_FILE_SETTINGS_NAME)

    def run(self, edit, highlight_types=None):
        self.logger.debug(highlight_types=highlight_types)

    def input(self, args):
        self.logger.debug(args)
        return HighlightTypesInputHandler(self.view, self.settings_file, self.logger)

class HighlightTypesInputHandler(commands_override.ListInputHandler):

    def name(self):
        return "highlight_types"

    def list_items(self):
        return [(ft.description, ft.name) for ft in HighlightTypes.all_members()]


    def confirm(self, highlight_type):
        self.logger.debug(highlight_type=highlight_type)
        view_utils.set_highlight_type(self.logger, self.view, self.settings, highlight_type)
        view_utils.filter(self.logger, self.view, view_utils.get_current_regex(self.logger, self.view, self.settings), view_utils.get_folding_type(self.logger, self.view, self.settings), view_utils.get_highlight_type(self.logger, self.view, self.settings))


##
##
## Clear Command
##
##

class ClearCommand(commands_override.WindowCommand):

    def __init__(self, window):
        super().__init__(window, SETTING_FILE_SETTINGS_NAME)

        self.view = self.window.active_view()

    def run(self):
        super().run()
        
        clear_settings = self.settings.get('on_clear_command_options', {})

        view_utils.clear(
            self.logger,
            self.view,
            unfold_regions = clear_settings.get('unfold_regions', True),
            remove_highlights = clear_settings.get('remove_highlights', True),
            center_viewport_on_carret = clear_settings.get('center_viewport_on_carret', True),
        )

##
##
## -
##
##
class FileFilterListener(sublime_plugin.EventListener):

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == KEY_MAP_CONTEXT_KEY_CLEAR:
            is_file_filter_active = view.settings().get(VIEW_SETTINGS_IS_FILTER_ACTIVE, False)
            LOGGER.debug(f"key: '{KEY_MAP_CONTEXT_KEY_CLEAR}, returning '{VIEW_SETTINGS_IS_FILTER_ACTIVE} -> {is_file_filter_active }")
            return is_file_filter_active
        return None