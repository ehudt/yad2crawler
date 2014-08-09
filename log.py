from settings           import LOG_LEVEL, LOG_FILE, LOG_FORMAT
from logging            import *


class Log(object):
    def __init__(self):
        self.logger = getLogger()
        self.logger.setLevel(LOG_LEVEL)

        log_formatter = Formatter(LOG_FORMAT, "%Y-%m-%d %H:%M:%S")

        file_handler = FileHandler(LOG_FILE)
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

        console_handler = StreamHandler()
        console_handler.setFormatter(log_formatter)
        self.logger.addHandler(console_handler)


    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)


    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)


    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)


    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)