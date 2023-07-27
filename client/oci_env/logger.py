# logger.py - reimplement some functionality of logzero

import logging
import os

# Define ANSI escape codes for different colors
ANSI_RESET = "\033[0m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"


# unique color per level
LOG_LEVEL_COLORS = {
    'DEBUG': ANSI_CYAN,
    'INFO': ANSI_GREEN,
    'WARNING': ANSI_YELLOW,
    'ERROR': ANSI_RED,
    'CRITICAL': ANSI_RED,
}


# need a custom class to have color per level
class LogColor(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super(LogColor, self).__init__(*args, **kwargs)
        self.log_color = LOG_LEVEL_COLORS[self.levelname]
        self.reset = ANSI_RESET


formatter = logging.Formatter('%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(filename)s:%(lineno)d - %(message)s')
logging.setLogRecordFactory(LogColor)
logger = logging.getLogger('oci_env')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


if os.environ.get("OCI_ENV_DEBUG"):
    logger.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)


# Add the console handler to the logger
logger.addHandler(console_handler)
