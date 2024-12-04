import logging
import os
from .utils import stringify

class CustomLogger(logging.Logger):
    
    def __init__(self, name, level=logging.INFO):
        super().__init__(name, level)
        self.info(f"[File Filter][CustomLogger] init")
        
        formatter = logging.Formatter(
            f"[FileFilter][%(levelname)3s][%(name)s.%(funcName)s():%(lineno)s]  %(message)s"
        )

        # Create and configure a StreamHandler
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        self.addHandler(self.stream_handler)

        if not bool(os.environ.get('STFileFilterEnv')):
            level = logging.ERROR
        
        self.setLevel(level)
        self.info(f"[File Filter] Creating logger with log level 'DEBUG' ({logging.DEBUG})")

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
