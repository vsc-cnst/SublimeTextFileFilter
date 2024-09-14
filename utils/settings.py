import sublime # type: ignore

class SettingsManager:
    def __init__(self, settings_file, logger=None):
        self.settings_file = settings_file
        self.logger = logger
        self.settings_key = f"{self.__class__.__name__}_{id(self)}"
        self.settings = sublime.load_settings(settings_file)
        self.settings.add_on_change(self.settings_key, self.reload_settings)
        self.reload_settings()

    def reload_settings(self):
        """
        Reloads the settings for this instance.

        Updates the internal state, logs the reload event if a logger is provided,
        and prints a message indicating the settings have been reloaded.
        """
        if self.logger:
            self.logger.info(f"Settings reloaded for {self.settings_key}")
        self.settings = sublime.load_settings(self.settings_file)

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
