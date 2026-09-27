import logging

import sublime # type: ignore
import sublime_plugin # type: ignore

from .custom_logger import CustomLogger # type: ignore
from .settings_manager import SettingsClient


class WindowCommand(sublime_plugin.WindowCommand, SettingsClient):
    
    def __init__(self, window):
        self.window = window

        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        sublime_plugin.WindowCommand.__init__(self, window)
        SettingsClient.__init__(self)


class TextCommand(sublime_plugin.TextCommand, SettingsClient):

    def __init__(self, view):
        self.view = view

        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        sublime_plugin.TextCommand.__init__(self, view)
        SettingsClient.__init__(self)



class ListInputHandler(sublime_plugin.ListInputHandler, SettingsClient):

    def __init__(self, view, logger:CustomLogger =None):
        self.view = view
        
        logger_name = "" if not logger else logger.name
        self.logger = logging.getLogger(f"{logger_name}.{self.__class__.__name__}")

        sublime_plugin.ListInputHandler.__init__(self)
        SettingsClient.__init__(self)

class TextInputHandler(sublime_plugin.TextInputHandler, SettingsClient):

    def __init__(self, view, logger=None):
        self.view = view
        
        logger_name = "" if not logger else logger.name
        self.logger = logging.getLogger(f"{logger_name}.{self.__class__.__name__}")
        
        sublime_plugin.TextInputHandler.__init__(self)
        SettingsClient.__init__(self)
