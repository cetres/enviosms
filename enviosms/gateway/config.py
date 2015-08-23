# -*- coding: UTF-8 -*-
""" Config
"""

import os
import logging
import urlparse

LOCAL_LOG_PATH = "/var/log/enviosms"
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
    _logger = None

    def __init__(self, app):
        self._root_path = app.root_path
        self._config = {}
        self._app = app
        self.mq_host = app.config.get("MQ_HOST")
        self.mq_addr = app.config.get("MQ_ADDR")
        self.mq_engine = app.config.get("MQ_ENGINE")

    def load_config(self, arquivo):
        arquivo = os.path.join(self._root_path, arquivo)
        if os.path.exists(arquivo):
            # self.logger
            # raise ConfigError("Arquivo nao encontrado: %s" % str(arquivo))
            execfile(arquivo, self._config)

    @property
    def mq_host(self):
        return self._config.get("mq_host")

    @mq_host.setter
    def mq_host(self, value):
        self._config["mq_host"] = value

    @property
    def mq_addr(self):
        return self._config.get("mq_addr")

    @mq_addr.setter
    def mq_addr(self, value):
        self._config["mq_addr"] = value

    @property
    def mq_url(self):
        return urlparse.urljoin(
            "%s://%s" % (self._config["mq_engine"], self._config["mq_host"]),
            self._config["mq_addr"])

    @mq_url.setter
    def mq_url(self, value):
        self._config["mq_url"] = value
        url = urlparse.urlparse(value)
        self._config["mq_engine"] = url.scheme.lower()
        self._config["mq_host"] = url.netloc.lower()
        self._config["mq_addr"] = url.path

    @property
    def timeout(self):
        return self._config.get("timeout")

    @timeout.setter
    def timeout(self, value):
        self._config["timeout"] = value

    @property
    def local_log_file(self):
        """Obtem o caminho para o arquivo local de log"""
        global LOCAL_LOG_PATH
        log_path = self._app.config.get("LOG_PATH", None)
        if not log_path:
            log_path = os.path.join(self._root_path, self._config.get("local_log_path", LOCAL_LOG_PATH))
        return log_path

    @property
    def debug(self):
        return self._app.debug

    def _logger_level(self):
        if self.debug:
            return logging.DEBUG
        global LOCAL_LOG_LEVEL
        return self._config.get("local_log_level", LOCAL_LOG_LEVEL)
        

    def _logger_handler_file(self):
        global LOCAL_LOG_FORMAT, LOCAL_LOG_LEVEL
        try:
            log_dir = ""
            if not self._log_handler:
                log_path = self.local_log_file
                log_dir = os.path.dirname(log_path)
                if not os.path.exists(log_dir):
                    logging.critical("Caminho de log nao existe. "
                                     "Tentando criar %s" % log_dir)
                    os.mkdir(log_dir)
                self._log_handler = logging.FileHandler(log_path)
                formatter = logging.Formatter(LOCAL_LOG_FORMAT)
                self._log_handler.setFormatter(formatter)
                log_level = self._config.get("local_log_level", LOCAL_LOG_LEVEL)
                self._log_handler.setLevel(log_level)
        except OSError:
            raise ConfigError("Impossivel criar pasta de log %s" % log_dir)
        return self._log_handler

    def logger(self, modulo):
        if not self._logger:
            self._app.logger.addHandler(self._logger_handler_file())
            self._app.logger.setLevel(self._logger_level())
            self._logger = self._app.logger
        return self._logger
