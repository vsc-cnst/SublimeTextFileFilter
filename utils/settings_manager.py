import sublime # type: ignore

from dataclasses import dataclass, field
import logging

from ..settings import SETTING_FILE_SETTINGS_NAME


class SettingsManager:

    settings_file: str
    settings_sublime: sublime.Settings
    settings: SettingsSnapshot

    def __init__(self, settings_file=SETTING_FILE_SETTINGS_NAME, logger=None):
        
        if settings_file is None:
            return
        
        self.settings_file = settings_file
        self.logger = logger or ( None if not hasattr(self, 'logger') else self.logger)
            
        self.settings_key = f"{self.__class__.__name__}_{id(self)}"
        
        self.settings_sublime = sublime.load_settings(settings_file)
        self.settings_sublime.add_on_change(self.settings_key, self.reload_settings)
        
        self.settings = SettingsSnapshot(self.settings_sublime)



    def reload_settings(self):
        """
        Reloads the settings for this instance.

        Updates the internal state, logs the reload event if a logger is provided,
        and prints a message indicating the settings have been reloaded.
        """
        if self.logger:
            self.logger.info(f"Settings reloaded for {self.settings_key}")
            
        self.settings = SettingsSnapshot(self.settings_sublime)

    def __del__(self):
        """
        Cleans up resources when the instance is deleted.

        Logs the cleanup event if a logger is provided, removes the settings
        change listener, and performs necessary cleanup operations.
        """
        if hasattr(self, 'settings') and self.settings:  # Check if settings exists
            if self.logger:
                self.logger.info(f"Cleaning up resources for {self.settings_key}")
            self.settings.clear_on_change(self.settings_key)


@dataclass
class SettingsSnapshot:
    global_settings: GlobalSettings
    defaults: DefaultsSettings 
    commands: CommandsSettings
    favorits: list
    expressions: list

    def __init__(self, settings: sublime.Settings):
        self.global_settings = GlobalSettings(settings.get('global', {}))
        self.defaults = DefaultsSettings(settings.get('defaults', {}))
        self.commands = CommandsSettings(settings.get('commands', {}))
        self.favorits = settings.get('favorits', [])
        self.expressions = settings.get('expressions', [])


@dataclass
class GlobalSettings:
    log_level: int = logging.ERROR
    global_regex_flags: str = "gi"

    def __init__(self, settings:dict):
        self.log_level = settings.get('log_level',self.log_level)
        self.global_regex_flags = settings.get('global_regex_flags', self.global_regex_flags)


@dataclass
class DefaultsSettings:
    highlight: HighlightDefaults
    folding: FoldingDefaults

    def __init__(self, settings:dict):
        self.highlight = HighlightDefaults(settings.get('highlight', {}))
        self.folding = FoldingDefaults(settings.get('folding', {}))


@dataclass
class HighlightDefaults:
    type: str = "solid"
    color: str = "white"

    def __init__(self, settings:dict):
        self.type = settings.get('type', self.type)
        self.color = settings.get('color', self.color)


@dataclass
class FoldingDefaults:
    type: str = "line"

    def __init__(self, settings:dict):
        self.type = settings.get('type', self.type)


@dataclass
class CommandsSettings:
    new: NewCommandSettings
    from_selection: FromSelectionSettings
    clear: ClearCommandSettings
    history: HistoryCommandSettings
    favorites: FavoritsCommandSettings

    def __init__(self, settings:dict):
        self.new = NewCommandSettings(settings.get('new', {}))
        self.from_selection = FromSelectionSettings(settings.get('from_selection', {}))
        self.clear = ClearCommandSettings(settings.get('clear', {}))
        self.history = HistoryCommandSettings(settings.get('history', {}))
        self.favorites = FavoritsCommandSettings(settings.get('favorites', {}))

@dataclass
class NewCommandSettings:
    filter_on_change: bool = False
    show_total_matches: bool = False

    def __init__(self, settings: dict):
        self.filter_on_change = settings.get('filter_on_change', self.filter_on_change)
        self.show_total_matches = settings.get('show_total_matches', self.show_total_matches)


@dataclass
class FromSelectionSettings:
    escape_selection: bool = False

    def __init__(self, settings: dict):
        self.escape_selection = settings.get('escape_selection', self.escape_selection)


@dataclass
class ClearCommandSettings:
    center_viewport_on_carret: bool = False
    remove_highlights: bool = False
    unfold_regions: bool = True

    def __init__(self, settings: dict):
        self.center_viewport_on_carret = settings.get('center_viewport_on_carret', self.center_viewport_on_carret)
        self.remove_highlights = settings.get('remove_highlights', self.remove_highlights)
        self.unfold_regions = settings.get('unfold_regions', self.unfold_regions)



@dataclass
class HistoryCommandSettings:

    def __init__(self, settings: dict):
        pass

    
@dataclass
class FavoritsCommandSettings:

    def __init__(self, settings: dict):
        pass