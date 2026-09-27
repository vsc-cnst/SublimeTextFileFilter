
import logging

import sublime # type: ignore

from .custom_logger import CustomLogger 
from .settings_manager_dataclasses import SettingsSnapshot

SETTINGS_FILE_NAME = 'file_filter.sublime-settings'

class SettingsManager:
    
    __instance: SettingsManager = None
    __initialized = False

    settings_sublime: sublime.Settings
    settings_snapshot: SettingsSnapshot
    
    logger: CustomLogger
    
    def __new__(cls):
        if not cls.__initialized:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        
        self.logger = logging.getLogger("Settings")

        self.settings_sublime = sublime.load_settings(SETTINGS_FILE_NAME)
        self.settings_snapshot = SettingsSnapshot(self.settings_sublime, logger=self.logger)
        self.settings_sublime.add_on_change("Settings", self.reload_settings)
        SettingsManager.__initialized = True

    def reload_settings(self):
        self.logger.info(f"Reloading settings.")
        self.settings_snapshot = SettingsSnapshot(self.settings_sublime, logger=self.logger)
        self.logger.info(f"Settings have been reloaded.")



ApplicationSettings = SettingsManager()


class SettingsClient:

    @property
    def settings(self) -> SettingsSnapshot:
        return ApplicationSettings.settings_snapshot

    def __init__(self):
        self.settings_key = f"{self.__class__.__name__}_{id(self)}"
        ApplicationSettings.settings_sublime.add_on_change(self.settings_key, self.reload_settings)

    def reload_settings(self):
        # to allow override
        pass

    def __del__(self):
        """
        Cleans up resources when the instance is deleted.
        """
        settings_key = getattr(self, "settings_key", None)
        if settings_key is not None:
            ApplicationSettings.settings_sublime.clear_on_change(settings_key)

