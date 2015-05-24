# -*- coding: UTF-8 -*-
""" Config
"""

import os
import logging

LOCAL_DB_PATH = "./dados"
LOCAL_DB_NAME = "orch"
LOCAL_LOG_PATH = "./logs/orch.log"
LOCAL_LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
LOCAL_LOG_LEVEL = logging.INFO


class ConfigError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class Config(object):
    _root_path = None
    _log_handler = None

    def __init__(self, app):
        self._root_path = app.root_path
        self._config = {}
        self._app = app

    def load_config(self, arquivo):
        arquivo = os.path.join(self._root_path, arquivo)
        if not os.path.exists(arquivo):
            raise ConfigError("Arquivo nao encontrado: %s" % str(arquivo))
        execfile(arquivo, self._config)

    @property
    def local_log_file(self):
        """Obtem o caminho para o arquivo local de log"""
        global LOCAL_LOG_PATH
        log_path = self._config.get("local_log_path", LOCAL_LOG_PATH)
        return os.path.join(self._root_path, log_path)

    @property
    def debug(self):
        return self._app.debug

    def _logger_handler_file(self):
        global LOCAL_LOG_FORMAT, LOCAL_LOG_LEVEL
        if not self._log_handler:
            log_path = self.local_log_file
            if not os.path.exists(log_path):
                try:
                    log_dir = os.path.dirname(log_path)
                    logging.critical("Caminho de log nao existe. "
                                     "Tentando criar %s" % log_dir)
                    os.mkdir(log_dir)
                except OSError:
                    raise ConfigError("Impossivel criar pasta de log")
            self._log_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter(LOCAL_LOG_FORMAT)
            self._log_handler.setFormatter(formatter)
            log_level = self._config.get("local_log_level", LOCAL_LOG_LEVEL)
            self._log_handler.setLevel(log_level)
        return self._log_handler

    def logger(self, modulo):
        global LOCAL_LOG_LEVEL
        logger = logging.getLogger(modulo)
        logger.addHandler(self._logger_handler_file())
        logger.setLevel(self._config.get("local_log_level", LOCAL_LOG_LEVEL))
        return logger