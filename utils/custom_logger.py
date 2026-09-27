import logging

# from .settings_manager import SETTINGS_FILE_NAME
SETTINGS_FILE_NAME = 'file_filter.sublime-settings'
from .utils import stringify

import sublime # type: ignore

TRACE = 5

class CustomLogger(logging.Logger):

    def __init__(self, name, level=logging.WARN):
        logging.Logger.__init__(self, name, level)

        
        self.settings = sublime.load_settings(SETTINGS_FILE_NAME)
        self.settings.add_on_change('CustomLogger_' + self.name, self.reload_settings)
        self.reload_settings()

        self.info(f"[File Filter][CustomLogger] init")
        self.propagate = False
        
        if not self.handlers:
            formatter = logging.Formatter(
                f"[FileFilter][%(levelname)3s][%(name)s.%(funcName)s():%(lineno)s]  %(message)s"
            )

            # Create and configure a StreamHandler
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setFormatter(formatter)
            self.addHandler(self.stream_handler)

        self.setLevel(level=level)

    def __del__(self):
        self.settings.settings_sublime.clear_on_change('CustomLogger_' + self.name)
        
    def reload_settings(self):
        self.level = self.settings.get('global', {}).get('log_level', self.level)
        self.setLevel(self.level)

    def setLevel(self, level):
        super().setLevel(level)
        self.info(f"Setting log_level to '{level}'")


    def trace(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().log(level=TRACE, msg=msg, stacklevel=2)

    def debug(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().debug(msg, stacklevel=2)

    def info(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().info(msg, stacklevel=2)

    def warning(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().warning(msg, stacklevel=2)

    def error(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().error(msg, stacklevel=2)

    def critical(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().critical(msg, stacklevel=2)

    def log(self, level, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().log(level, msg, stacklevel=2)

    def __del__(self):
        self.close()
        
    def close(self):
        self.debug(f"Logger '{self.name}' is closing. Removing all {len(self.handlers)} handlers.")

        # Close and remove the handler
        for handler in self.handlers[:]:
            handler.close()
            self.removeHandler(handler)

        self.stream_handler = None
