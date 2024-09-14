import logging

import sublime # type: ignore
import sublime_plugin # type: ignore

from .settings import SettingsManager


class WindowCommand(sublime_plugin.WindowCommand, SettingsManager):
    
    def __init__(self, window, settings_file):
        super().__init__(window)
        self.logger = logging.getLogger(f"FileFilter.{self.__class__.__name__}")

        sublime_plugin.WindowCommand.__init__(self, window)
        SettingsManager.__init__(self, settings_file, logger=self.logger)

class TextCommand(sublime_plugin.TextCommand, SettingsManager):

    def __init__(self, view, settings_file):
        super().__init__(view)
        self.logger = logging.getLogger(f"FileFilter.{self.__class__.__name__}")

        sublime_plugin.TextCommand.__init__(self, view)
        SettingsManager.__init__(self, settings_file, logger=self.logger)


class ListInputHandler(sublime_plugin.ListInputHandler, SettingsManager):

    def __init__(self, view, settings_file, logger=None):

        self.view = view

        logger_name = "" if not logger else logger.name
            
        self.logger = logging.getLogger(f"FileFilter.{logger_name}.{self.__class__.__name__}")

        sublime_plugin.ListInputHandler.__init__(self)
        SettingsManager.__init__(self, settings_file, logger=self.logger)


class TextInputHandler(sublime_plugin.TextInputHandler, SettingsManager):

    def __init__(self, view, settings_file, logger=None):

        self.view = view
        
        logger_name = "" if not logger else logger.name
        self.logger = logging.getLogger(f"FileFilter.{logger_name}.{self.__class__.__name__}")
        
        sublime_plugin.TextInputHandler.__init__(self)
        SettingsManager.__init__(self, settings_file, logger=self.logger)
