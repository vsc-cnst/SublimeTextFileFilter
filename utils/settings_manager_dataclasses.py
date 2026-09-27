from dataclasses import dataclass
import logging

from .expression import Expression

import sublime # type: ignore

@dataclass
class SettingsSnapshot:
    global_settings: GlobalSettings
    defaults: DefaultsSettings 
    commands: CommandsSettings
    favorits: list[Expression]
    expressions: list[Expression]

    def __init__(self, settings: sublime.Settings, logger=None):
        self.global_settings = GlobalSettings(settings.get('global', {}))
        self.defaults = DefaultsSettings(settings.get('defaults', {}))
        self.commands = CommandsSettings(settings.get('commands', {}))

        self.favorits = []
        self.expressions = []
        
        
        for fav in settings.get('favorits', []) :
            if not isinstance(fav, dict) or not fav.get('code', []) or not fav.get('pattern', []):
                logger.error("Could not load favorit. Must be a dictionary with properties 'code' and 'pattern'")
                continue

            self.favorits.append( 
                Expression.new(
                    data=fav.get('pattern'),
                    code=fav.get('code'),
                    name=fav.get('name'),
                    type=fav.get('type', None),
                    color=fav.get('color', None),
                    escape=fav.get('escape', None),
                    logger=logger
                )
            )

                
        # self.expressions = [Expression.new(expression, logger=logger) for expression in settings.get('expressions', [])]


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

