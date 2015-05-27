# -*- coding: UTF-8 -*-
import abc
from urlparse import urlparse
import json
import logging

from .qpid import Qpid
from .sqs import SQS

logger = logging.getLogger("enviosms")


class MQError(Exception):
    _errors = {
        1: "Classe com a URI nao encontrada",
        2: "Nao foi possivel realizar conexao na fila",
    }

    def __init__(self, msg=None, cod=0):
        if not msg:
            self.msg = self._errors[cod]
        else:
            self.msg = msg
        self.cod = cod

    def __str__(self):
        return self.msg


class MQ(object):
    """
    Classe abstrata responsavel por interagir com o sistema MQ

    Ao implementar outra classe de MQ sera preciso repensar
        a estrategia de tratamento da mensagem ativa

    """

    __metaclass__ = abc.ABCMeta
    _url = None
    _config = None
    _logger = None
    _conn = None
    _queue = None

    def __init__(self, url, config):
        self._url = MQ.urlparse(url)
        self._config = config
        self._logger = self._config.logger(self.__class__.__name__)
        self._logger.debug("Instanciando Queue Helper")
        self.conectar()

    @abc.abstractmethod
    def _conectar(self):
        """ Metodo para estabelecimento de conexao com o MQ """

    def conectar(self):
        if not self._queue:
        	self._conectar()

    def enviar(self, mensagem, formato=None):
        self.conectar()
        if formato:
            if formato.lower() == "json":
                mensagem = json.dumps(mensagem)
        return self._enviar(mensagem)

    @abc.abstractmethod
    def _enviar(self, mensagem):
        """Metodo para envio de mensagem a MQ """

    def receber(self, formato=None):
        self.conectar()
        mensagem = self._receber()
        if formato and mensagem:
            if formato.lower() == "json":
                mensagem = json.loads(mensagem)
        return mensagem

    @abc.abstractmethod
    def _receber(self):
        """Metodo para recebimento de mensagem da MQ """

    def excluir(self):
        self.conectar()
        return self._excluir()

    @abc.abstractmethod
    def _excluir(self):
        """Metodo para exclusao de mensagem da MQ """

    def tamanho(self):
        self.conectar()
        return self._tamanho()

    @abc.abstractmethod
    def _tamanho(self):
        """Metodo para obter o tamanho do MQ """

    @staticmethod
    def urlparse(url):
        return urlparse(url)


def mq_from_url(url):
    scheme = MQ.urlparse(url).scheme.lower()
    if scheme == "qpid":
        return Qpid
    else:
        raise MQError(None, 1)

__all__ = ['Qpid', 'SMS', 'MQError', 'mq_from_url']