from __future__ import absolute_import
from __future__ import unicode_literals
import logging
import os
import sys

LOCAL_LOG_NAME = "enviosms"
LOCAL_LOG_PATH = "/var/logs/enviosms"
LOCAL_LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
LOCAL_LOG_LEVEL = logging.INFO

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG


class MaxLevelFilter(object):
    def __init__(self, max_level):
        self.max_level = max_level

    def filter(self, record):
        if record.levelno >= self.max_level:
            return 0
        return 1


def only_once(func):
    """Method decorator turning the method into noop on second or later calls."""
    def noop(*_args, **_kwargs):
        pass

    def swan_song(self, *args, **kwargs):
        func(self, *args, **kwargs)
        setattr(self, func.__name__, noop)
    return swan_song


class Logging(object):
    _logger = None
    _stdout_handler = None
    _stderr_handler = None
    _logfile_handler = None
    local_log_path = LOCAL_LOG_PATH

    def __init__(self, log_level=LOCAL_LOG_LEVEL):
        global LOCAL_LOG_NAME
        self._logger = logging.getLogger(LOCAL_LOG_NAME)

    def _logger_handler_file(self, log_level, log_path=None):
        global LOCAL_LOG_FORMAT
        if not self._logfile_handler:
            if not log_path:
                log_path = self.local_log_path
            if not os.path.exists(log_path):
                try:
                    log_dir = os.path.dirname(log_path)
                    logging.critical("Caminho de log nao existe. "
                                     "Tentando criar %s" % log_dir)
                    os.mkdir(log_dir)
                except OSError:
                    raise
            self._logfile_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter(log_level)
            self._logfile_handler.setFormatter(formatter)
            self._logfile_handler.setLevel(log_level)
        return self._logfile_handler

    @property
    def logger(self):
        return self._logger

    @only_once
    def _setup(self, log_level, log_path=None):
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(INFO)
        stdout.addFilter(MaxLevelFilter(logging.WARNING))
        self._logger.addHandler(stdout)
        self._stdout_handler = stdout

        stderr = logging.StreamHandler(sys.stderr)
        stderr.setLevel(WARNING)
        self._logger.addHandler(stderr)
        self._stderr_handler = stderr

        if log_path:
            self._logger.addHandler(self._logger_handler_file(log_level, log_path))

        self._logger.setLevel(log_level)

    @staticmethod
    def getLogger():
        global LOCAL_LOG_NAME
        return logging.getLogger(LOCAL_LOG_NAME)

    @staticmethod
    def setup(log_level=LOCAL_LOG_LEVEL, log_path=None):
        logger_sms = Logging()
        logger_sms._setup(log_level, log_path)
        return logger_sms.logger
