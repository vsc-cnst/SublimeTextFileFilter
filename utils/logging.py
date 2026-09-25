import logging

from .settings_manager import SettingsManager
from .utils import stringify

class CustomLogger(logging.Logger, SettingsManager):

    
    def __init__(self, name, level=logging.WARN):
        super().__init__(name, level)
        SettingsManager.__init__(self)
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

        self.setLevel(self.settings.get('log_level', level))

    def load_settings(self):
        super().load_settings()
        lvl = self.settings.get('log_level', logging.WARN)
        self.setLevel(lvl)

    def setLevel(self, level=logging.WARN):
        super().setLevel(level)
        self.info(f"[File Filter] Creating logger with log level '{level}'")
    
    def trace(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().log(level=1, msg=msg, stacklevel=2)

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
