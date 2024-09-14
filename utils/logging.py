import logging
import os

from .utils import stringify

class CustomLogger(logging.Logger):

    def __init__(self, name, level=logging.INFO):
        super().__init__(name, level)
        
        formatter = logging.Formatter(f"[%(levelname)3s][%(name)s.%(funcName)s():%(lineno)s]  %(message)s" )

        # Create and configure a StreamHandler
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        self.addHandler(self.stream_handler)

        self.setLevel(level)


        if bool(os.environ.get('STFileFilterEnv')):
            self.setLevel(logging.DEBUG)
        else:
            self.setLevel(logging.ERROR)

        self.info(f"creating logger with log level 'DEBUG' ({logging.DEBUG})")
        # Set default logging level

    def debug(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().debug(msg)

    def info(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().info(msg)

    def warning(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().warning(msg)

    def error(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().error(msg)

    def critical(self, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().critical(msg)

    def log(self, level, *args, **kwargs):
        msg = stringify(*args, **kwargs)
        super().log(level, msg)

    def __del__(self):
        self.close()
        
    def close(self):

        self.debug(f"Logger '{self.name}' is closing. Removing all {len(self.handlers)} handlers.")

        # Close and remove the handler
        for handler in self.handlers[:]:
            handler.close()
            self.removeHandler(handler)

        self.stream_handler = None