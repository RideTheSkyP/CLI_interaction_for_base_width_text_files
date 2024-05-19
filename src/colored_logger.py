import logging

# Colors in ANSI format(without installing external software) for logging
RESET = '\033[0m'
COLORS = {
    'DEBUG': '\033[94m',    # Blue
    'INFO': '\033[92m',     # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',    # Red
    'CRITICAL': '\033[95m'  # Magenta
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        log_fmt = COLORS.get(record.levelname, '') + self._fmt + RESET
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger():
    log_format = '%(levelname)s: %(message)s'
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    colored_formatter = ColoredFormatter(log_format)
    console_handler.setFormatter(colored_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()
