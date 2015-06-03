# -*- coding: UTF-8 -*-
import logging

from qpid.messaging import Connection, Message
from qpid.messaging.exceptions import ConnectError

from enviosms.mq import MQ, MQError

logger = logging.getLogger("enviosms")

class Qpid(MQ):
    _timeout = 1
    def _conectar(self):
        try:
            self._logger.debug("Regiao AWS: %s" % self._url.netloc)
            self._conn = Connection(self._url.netloc)
            if not self._conn:
                raise MQError(None, 2)
            self._conn.open()
            self._session = self._conn.session()
            self._sender = self._session.sender(self._url.path[1:])
            self._receiver = self._session.receiver(self._url.path[1:])
        except ConnectError as e:
            raise MQError(2)

    def _enviar(self, mensagem):
        m = Message(mensagem)
        self._sender.send(m, True, self._timeout)

    def _receber(self, timeout=None):
        self._mensagem = self._receiver.fetch(timeout)
        return self._mensagem.content

    def _tamanho(self):
        self._receiver.available()

    def _excluir(self):
        self._session.acknowledge()
    
    def _terminar(self):
        self._conn.close(self._timeout)
